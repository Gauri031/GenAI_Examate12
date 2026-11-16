"""Run semantic search for every question in eval/questions.txt and write eval/search_results.md.

Run from the day07 folder:   python eval/run_search.py
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.embed import EMBED_MODEL  # noqa: E402
from app.vectorstore import get_collection, index_all, semantic_search  # noqa: E402

TOP_K = 3

questions = [q.strip() for q in (ROOT / "eval" / "questions.txt").read_text(encoding="utf-8").splitlines() if q.strip()]

if get_collection().count() == 0:
    print("Index is empty, building it first...")
    index_all(reset=True)
total_chunks = get_collection().count()


def clean(text: str, limit: int = 170) -> str:
    text = " ".join(str(text).replace("|", "/").split())
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


results = []
for i, q in enumerate(questions, 1):
    print(f"Q{i}/{len(questions)}: {q}")
    results.append((i, q, semantic_search(q, TOP_K)))

out = [
    "# Semantic Search Results", "",
    f"- Date: {date.today().isoformat()}",
    f"- Embedding model: {EMBED_MODEL}",
    f"- Chunks in index: {total_chunks}",
    f"- Top {TOP_K} hits per question. Score = cosine similarity (higher = closer in meaning).", "",
    "## Summary (top-1 hit per question)", "",
    "| # | Question | Top source | Page | Score | Relevant? (Y/N) |",
    "|---|----------|------------|------|-------|-----------------|",
]
for i, q, hits in results:
    if hits:
        h = hits[0]
        out.append(f"| {i} | {clean(q, 80)} | {h['source']} | {h['page']} | {h['score']} | [EDIT] |")
    else:
        out.append(f"| {i} | {clean(q, 80)} | - | - | - | N |")

out += ["", "## All hits", ""]
for i, q, hits in results:
    out += [f"### Q{i}. {q}", "",
            "| Rank | Score | Source | Page | Title | Snippet |",
            "|------|-------|--------|------|-------|---------|"]
    for h in hits:
        out.append(f"| {h['rank']} | {h['score']} | {h['source']} | {h['page']} | {clean(h['title'], 40)} | {clean(h['text'])} |")
    out.append("")

out += ["## My analysis (EDIT: write in your own words)", "",
        "- **Questions where the top hit was clearly right:** [EDIT]",
        "- **Questions where search missed or was weak, and why:** [EDIT]",
        "- **Q6 (data cannot answer): what did search return and what were the scores?** [EDIT]",
        "- **What I would change (chunk size, more documents, etc.):** [EDIT]", ""]

(ROOT / "eval" / "search_results.md").write_text("\n".join(out), encoding="utf-8")
print("Saved eval/search_results.md")
