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


def safe(question: str, version: str) -> dict:
    try:
        return run_prompt(question, version)
    except Exception as exc:  # keep going if one call fails
        return {"answer": f"ERROR: {exc}", "confidence": "-", "follow_up": "-"}


rows = []
for i, q in enumerate(questions, 1):
    print(f"Q{i}/{len(questions)}: {q}")
    rows.append((i, q, safe(q, "v1"), safe(q, "v2")))

out = ["# Prompt Comparison: v1 vs v2", "",
       "Both prompts use the same `prompts/system.md`. Only the task prompt differs.", "",
       "- **v1** (`prompts/task_v1.md`): short, plain instruction.",
       "- **v2** (`prompts/task_v2.md`): structured instruction with answer-length limit, confidence rules and a follow-up requirement.", "",
       "## Results on my 10 questions", "",
       "| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. | v2 follow_up |",
       "|---|----------|-----------|----------|-----------|----------|--------------|"]
for i, q, a, b in rows:
    out.append(f"| {i} | {clean(q)} | {clean(a['answer'])} | {a['confidence']} | {clean(b['answer'])} | {b['confidence']} | {clean(b['follow_up'])} |")

out += ["", "## My analysis (EDIT: write in your own words)", "",
        "- **Which prompt was better overall and why?** [EDIT]",
        "- **How did each handle Q6 (data cannot answer)?** [EDIT]",
        "- **Was the confidence value sensible?** [EDIT]",
        "- **Were the follow-up questions useful?** [EDIT]",
        "- **Which prompt I chose for /chat (default) and why:** v2 [EDIT if different]", ""]

(ROOT / "eval" / "prompt_compare.md").write_text("\n".join(out), encoding="utf-8")
print("Saved eval/prompt_compare.md")
