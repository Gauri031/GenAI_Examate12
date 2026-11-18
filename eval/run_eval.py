"""Evaluate the PoshanGuide RAG pipeline with 2 configurations on eval/eval_set.json.

Configurations differ in chunk size and top-k (edit CONFIGS below).
Run from the day08 folder:   python eval/run_eval.py

Outputs
  eval/eval_results.md   every question, answer, citations and pass/fail for both configs
  README.md              the winner table is written between the EVAL_TABLE markers
"""
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.rag import answer_question  # noqa: E402
from app.vectorstore import get_collection, index_all  # noqa: E402

CONFIGS = [
    {"name": "A", "chunk_size": 400, "top_k": 3},
    {"name": "B", "chunk_size": 700, "top_k": 5},
]

EVAL_SET = ROOT / "eval" / "eval_set.json"
RESULTS_MD = ROOT / "eval" / "eval_results.md"
README = ROOT / "README.md"
START, END = "<!-- EVAL_TABLE_START -->", "<!-- EVAL_TABLE_END -->"
PAUSE = 0.4  # seconds between LLM calls (free tiers have rate limits)


def is_idk(answer: str) -> bool:
    a = answer.strip().lower()
    return a.startswith("i don't know") or a.startswith("i do not know") or a.startswith("i don’t know")


def ask_with_retry(question: str, cfg: dict) -> dict:
    """Call the RAG pipeline, retry up to 3 times. Never raises: errors are returned as a result."""
    last = None
    for attempt in range(1, 4):
        try:
            return answer_question(question, top_k=cfg["top_k"], max_chars=cfg["chunk_size"])
        except Exception as exc:  # provider or JSON problem
            last = exc
            time.sleep(2 * attempt)
    return {"answer": f"ERROR: {last}", "answerable": False, "citations": [], "retrieved": [], "error": True}


def score_row(row: dict, result: dict) -> dict:
    """Decide pass/fail for one question."""
    if result.get("error"):
        return {"passed": False, "idk": None, "retrieval_hit": None, "cited_ok": None, "keyword_ok": None, "error": True}
    answer = result["answer"]
    idk = (not result["answerable"]) or is_idk(answer)
    if not row["answerable"]:  # Q6-type: the only correct behaviour is "I don't know"
        return {"passed": idk, "idk": idk, "retrieval_hit": None, "cited_ok": None, "keyword_ok": None, "error": False}
    retrieved = {r["source"] for r in result["retrieved"]}
    cited = {c["source"] for c in result["citations"]}
    hit = row["expected_source"] in retrieved
    cited_ok = row["expected_source"] in cited
    keyword_ok = any(k.lower() in answer.lower() for k in row["expected_keywords"])
    return {
        "passed": (not idk) and cited_ok and keyword_ok,
        "idk": idk, "retrieval_hit": hit, "cited_ok": cited_ok, "keyword_ok": keyword_ok, "error": False,
    }


def run_config(cfg: dict, rows: list[dict]) -> dict:
    info = index_all(reset=True, max_chars=cfg["chunk_size"])
    print(f"\n=== Config {cfg['name']}: chunk size {cfg['chunk_size']}, top-k {cfg['top_k']} ({info['chunks']} chunks) ===")
    records, seconds = [], []
    for row in rows:
        start = time.time()
        result = ask_with_retry(row["question"], cfg)
        seconds.append(time.time() - start)
        score = score_row(row, result)
        records.append({"row": row, "result": result, "score": score})
        print(f"{row['id']}: {'PASS' if score['passed'] else 'FAIL'}  {row['question']}")
        time.sleep(PAUSE)

    answerable = [r for r in records if r["row"]["answerable"]]
    unanswerable = [r for r in records if not r["row"]["answerable"]]
    return {
        "cfg": cfg,
        "chunks": get_collection(cfg["chunk_size"]).count(),
        "records": records,
        "total": len(records),
        "passed": sum(r["score"]["passed"] for r in records),
        "answerable_total": len(answerable),
        "retrieval_hits": sum(bool(r["score"]["retrieval_hit"]) for r in answerable),
        "citation_ok": sum(bool(r["score"]["cited_ok"]) for r in answerable),
        "false_refusals": sum(bool(r["score"]["idk"]) for r in answerable),
        "unanswerable_total": len(unanswerable),
        "correct_idk": sum(bool(r["score"]["passed"]) for r in unanswerable),
        "avg_seconds": sum(seconds) / len(seconds) if seconds else 0.0,
    }


def pick_winner(summaries: list[dict]) -> dict:
    """Most passes wins; tie -> more retrieval hits; tie -> smaller top-k (cheaper)."""
    return max(summaries, key=lambda s: (s["passed"], s["retrieval_hits"], -s["cfg"]["top_k"]))


def make_table(summaries: list[dict]) -> str:
    winner = pick_winner(summaries)
    lines = [
        "| Config | Chunk size | Top-k | Chunks | Pass | Retrieval hit | Citation ok | Correct \"I don't know\" | False refusals | Avg sec/question |",
        "|--------|-----------|-------|--------|------|---------------|-------------|------------------------|----------------|------------------|",
    ]
    for s in summaries:
        c = s["cfg"]
        mark = " **(winner)**" if s is winner else ""
        lines.append(
            f"| {c['name']}{mark} | {c['chunk_size']} | {c['top_k']} | {s['chunks']} "
            f"| {s['passed']}/{s['total']} ({100 * s['passed'] // s['total']}%) "
            f"| {s['retrieval_hits']}/{s['answerable_total']} "
            f"| {s['citation_ok']}/{s['answerable_total']} "
            f"| {s['correct_idk']}/{s['unanswerable_total']} "
            f"| {s['false_refusals']}/{s['answerable_total']} "
            f"| {s['avg_seconds']:.1f} |"
        )
    c = winner["cfg"]
    lines += ["", f"**Winner: Config {c['name']}** (chunk size {c['chunk_size']}, top-k {c['top_k']}) "
                  f"with {winner['passed']}/{winner['total']} questions passed.",
              "", f"_Run on {date.today().isoformat()}._"]
    return "\n".join(lines)


def clean(text: str, limit: int = 300) -> str:
    text = " ".join(str(text).replace("|", "/").split())
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def write_results(summaries: list[dict], table: str) -> None:
    out = ["# RAG Evaluation Results", "", "## Winner table", "", table, ""]
    for s in summaries:
        c = s["cfg"]
        out += [f"## Config {c['name']} (chunk size {c['chunk_size']}, top-k {c['top_k']})", "",
                "| ID | Question | Expected | Result | Answer | Cited sources | Pass |",
                "|----|----------|----------|--------|--------|---------------|------|"]
        for rec in s["records"]:
            row, res, sc = rec["row"], rec["result"], rec["score"]
            expected = row["expected_source"] or "I don't know"
            got = "ERROR" if sc.get("error") else ("I don't know" if sc["idk"] else "answered")
            cited = ", ".join(f"{x['source']} p{x['page']}" for x in res.get("citations", [])) or "-"
            out.append(f"| {row['id']} | {clean(row['question'], 80)} | {expected} | {got} "
                       f"| {clean(res['answer'])} | {cited} | {'PASS' if sc['passed'] else 'FAIL'} |")
        out.append("")
    out += ["## How pass/fail is decided", "",
            "- **Answerable question:** passes if the answer is not \"I don't know\", cites the expected source file, and contains at least one expected keyword.",
            "- **Unanswerable question:** passes only if the answer is \"I don't know\".",
            "- The keyword check is a rough automatic proxy. Read the answers above to double-check it.", ""]
    RESULTS_MD.write_text("\n".join(out), encoding="utf-8")


def update_readme(table: str) -> bool:
    if not README.exists():
        return False
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return False
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), f"{START}\n{table}\n{END}", text, flags=re.DOTALL)
    README.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    rows = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    if len(rows) != 15:
        print(f"Warning: the task asks for 15 rows, eval_set.json has {len(rows)}.")
    summaries = [run_config(cfg, rows) for cfg in CONFIGS]
    table = make_table(summaries)
    write_results(summaries, table)
    print("\n" + table)
    print(f"\nSaved {RESULTS_MD.relative_to(ROOT)}")
    print("README.md winner table updated." if update_readme(table)
          else "README.md markers not found: copy the table above into the README yourself.")


if __name__ == "__main__":
    main()
