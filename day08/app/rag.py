"""RAG: answer PoshanGuide questions from retrieved chunks, with citations (Day 08).

Flow:  question -> semantic_search (top_k chunks) -> prompt with numbered passages
       -> LLM returns JSON {answerable, answer, sources}
       -> citations are built from the passages the model used
       -> if the documents do not contain the answer, reply "I don't know".
"""
import os
import re
from pathlib import Path

from app.llm import call_llm, parse_json
from app.vectorstore import DEFAULT_CHUNK, semantic_search

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

TOP_K = 4
# Chunks with a lower cosine score than this are not even shown to the model.
MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.20"))

IDK_ANSWER = (
    "I don't know. I could not find this in the PoshanGuide documents. "
    "Please ask your Anganwadi worker, ASHA worker or the nearest health centre."
)


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _build_context(hits: list[dict]) -> str:
    blocks = []
    for n, h in enumerate(hits, 1):
        blocks.append(f"[{n}] (source: {h['source']}, page {h['page']}, title: {h['title']})\n{h['text']}")
    return "\n\n".join(blocks)


def _is_idk(answer: str) -> bool:
    a = answer.strip().lower()
    return a.startswith("i don't know") or a.startswith("i do not know") or a.startswith("i don’t know")


def _result(question, answer, answerable, citations, retrieved, top_k, chunk_size):
    return {
        "question": question,
        "answer": answer,
        "answerable": answerable,
        "citations": citations,
        "retrieved": retrieved,
        "config": {"top_k": top_k, "chunk_size": chunk_size},
    }


def answer_question(
    question: str,
    top_k: int = TOP_K,
    max_chars: int = DEFAULT_CHUNK,
    min_score: float = MIN_SCORE,
) -> dict:
    """Answer one question from the documents. Raises LLMError / ValueError on provider problems."""
    hits = semantic_search(question, top_k, max_chars)
    retrieved = [{"source": h["source"], "page": h["page"], "score": h["score"]} for h in hits]

    usable = [h for h in hits if h["score"] >= min_score]
    if not usable:  # nothing even close: do not call the LLM
        return _result(question, IDK_ANSWER, False, [], retrieved, top_k, max_chars)

    system = _load_prompt("rag_system.md")
    task = (
        _load_prompt("rag_task.md")
        .replace("{context}", _build_context(usable))
        .replace("{question}", question)
    )
    data = parse_json(call_llm(system, task, temperature=0.0))

    answerable = str(data.get("answerable", "")).strip().lower() in {"true", "yes", "1"}
    answer = str(data.get("answer", "")).strip()

    numbers = []
    for n in data.get("sources", []) or []:
        try:
            numbers.append(int(n))
        except (TypeError, ValueError):
            pass
    if not numbers:  # fall back to [n] marks written inside the answer
        numbers = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
    numbers = sorted({n for n in numbers if 1 <= n <= len(usable)})

    # An answer without a valid citation, or a refusal, becomes "I don't know".
    if not answerable or not answer or _is_idk(answer) or not numbers:
        return _result(question, IDK_ANSWER, False, [], retrieved, top_k, max_chars)

    citations = []
    for n in numbers:
        h = usable[n - 1]
        snippet = " ".join(h["text"].split())
        citations.append(
            {
                "id": n,
                "source": h["source"],
                "page": h["page"],
                "title": h["title"],
                "score": h["score"],
                "snippet": snippet[:200] + ("..." if len(snippet) > 200 else ""),
            }
        )
    return _result(question, answer, True, citations, retrieved, top_k, max_chars)
