"""Small tools an agent can call (Day 11: covered by tests/test_agent_tool.py).

  search_documents(query, k)  find the PoshanGuide document chunks closest to a query
  nin_plate_amounts()         the ICMR-NIN "My Plate for the Day" amounts (grams per day)

If your Day 09 agent has its own tools, add them to TOOLS and test them the same way.
"""
import json
from pathlib import Path

from app.vectorstore import semantic_search

PLATE_FILE = Path(__file__).resolve().parent.parent / "data" / "plate_reference.json"


def search_documents(query: str, k: int = 3) -> list[dict]:
    """Return the k closest chunks as small dicts: source, page, title, score, text."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    hits = semantic_search(query.strip(), k)
    return [
        {"source": h["source"], "page": h["page"], "title": h["title"], "score": h["score"], "text": h["text"]}
        for h in hits
    ]


def nin_plate_amounts() -> dict:
    """Return {food group: grams per day} for the 2000 kcal NIN plate."""
    reference = json.loads(PLATE_FILE.read_text(encoding="utf-8"))
    return {g["key"]: g["target_g"] for g in reference["groups"]}


TOOLS = {
    "search_documents": search_documents,
    "nin_plate_amounts": nin_plate_amounts,
}


def run_tool(name: str, **kwargs):
    """Run a tool by name. Unknown names raise KeyError."""
    if name not in TOOLS:
        raise KeyError(f"Unknown tool: {name}")
    return TOOLS[name](**kwargs)
