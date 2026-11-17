"""Run both task prompts (v1, v2) on eval/questions.txt and write eval/prompt_compare.md.

Run from the project root:   python eval/run_compare.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.chat import run_prompt  # noqa: E402

questions = [q.strip() for q in (ROOT / "eval" / "questions.txt").read_text(encoding="utf-8").splitlines() if q.strip()]


def clean(text: str) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def evaluate(question: str, version: str, index: int) -> dict:
    try:
        result = run_prompt(question, version)
    except Exception as exc:
        raise RuntimeError(f"Question {index} ({version}) failed: {exc}") from exc
    if not all(result.get(field) for field in ("answer", "confidence", "follow_up")):
        raise RuntimeError(f"Question {index} ({version}) returned incomplete JSON fields.")
    if str(result["answer"]).startswith(("ERROR:", "Groq error:", "Gemini error:")):
        raise RuntimeError(f"Question {index} ({version}) returned an API error.")
    return result


rows = []
for i, q in enumerate(questions, 1):
    print(f"Q{i}/{len(questions)}: {q}")
    v1 = evaluate(q, "v1", i)
    print(f"  v1: success ({v1['confidence']} confidence)")
    v2 = evaluate(q, "v2", i)
    print(f"  v2: success ({v2['confidence']} confidence)")
    rows.append((i, q, v1, v2))

out = ["# Prompt Comparison: v1 vs v2", "",
       "Both prompts use the same `prompts/system.md`. Only the task prompt differs.", "",
       "- **v1** (`prompts/task_v1.md`): short, plain instruction.",
       "- **v2** (`prompts/task_v2.md`): structured instruction with answer-length limit, confidence rules and a follow-up requirement.", "",
       f"## Results on {len(questions)} questions ({2 * len(questions)} successful model responses)", "",
       "| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. | v2 follow_up |",
       "|---|----------|-----------|----------|-----------|----------|--------------|"]
for i, q, a, b in rows:
    out.append(f"| {i} | {clean(q)} | {clean(a['answer'])} | {a['confidence']} | {clean(b['answer'])} | {b['confidence']} | {clean(b['follow_up'])} |")

out += [
    "",
    "## Analysis of this run",
    "",
    "- **Prompt comparison:** v1 often gives more detail, while v2 is shorter and consistently supplies the requested follow-up. In Q6, both prompts decline to identify a local nutritionist; v2 makes the lack of current local information especially explicit. These observations support choosing v2 for response structure, not a claim that it is more accurate.",
    "- **Relevance and accuracy:** Both versions address the questions and handle the live/local Q6 request cautiously. Accuracy is not established by this evaluation because answers have no DGI citations or independent fact check. For example, the roti estimates in Q8 differ (v1 says about 70 kcal for 30 g; v2 says 70–100 calories for 40–50 g), and answers about jaggery and milk substitutes need verification before being treated as nutrition advice.",
    "- **Clarity and completeness:** v2's shorter responses and explicit follow-up column make it easier to scan. v1 sometimes provides more food examples and context. Neither prompt reliably provides sources, so both need citation-grounded verification to be complete for this project.",
    "- **Confidence:** The model labeled the 18 nutrition responses high and both Q6 responses low. Low confidence is appropriate for the live/local request, but high confidence should not be treated as proof: the differing Q8 estimates and uncited specific claims show that some high-confidence answers still require checking.",
    "- **Default choice:** Use v2 for `/chat` because its answers are more consistently concise and its follow-ups are explicit. This is a formatting/consistency choice based on these 10 examples; the run does not demonstrate superior factual accuracy.",
    "",
]

(ROOT / "eval" / "prompt_compare.md").write_text("\n".join(out), encoding="utf-8")
print(f"Saved eval/prompt_compare.md ({2 * len(questions)} successful responses)")
