"""PoshanGuide - main FastAPI app.

Endpoints
  GET  /        welcome message
  GET  /health  simple health check
  GET  /ask     answer from our own data (Day 05)
  POST /chat    answer from the LLM, returns answer/confidence/follow_up (Day 06, see app/chat.py)

Run from the project root:  uvicorn app.main:app --reload
"""
import json
from pathlib import Path

from fastapi import FastAPI

from app.chat import router as chat_router

app = FastAPI(
    title="PoshanGuide",
    description="Nutrition guidance for families, answered from our own data and an LLM.",
)
app.include_router(chat_router)

ROOT = Path(__file__).resolve().parent.parent
# Looks for the data file in these places, first one found is used.
DATA_CANDIDATES = [
    ROOT / "data" / "nutrition.json",
    ROOT / "day02" / "data" / "nutrition.json",
]


def load_data() -> list[dict]:
    """Read the nutrition data file once at startup. Returns [] if not found."""
    for path in DATA_CANDIDATES:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return []


DATA = load_data()


def find_answer(question: str) -> str | None:
    """Return the answer of the entry with the most keyword matches, or None.

    Expects each entry like: {"keywords": ["iron", "anaemia"], "answer": "..."}
    """
    q = question.lower()
    best, best_score = None, 0
    for entry in DATA:
        if not isinstance(entry, dict) or "keywords" not in entry or "answer" not in entry:
            continue
        score = sum(1 for kw in entry["keywords"] if kw.lower() in q)
        if score > best_score:
            best, best_score = entry["answer"], score
    return best


@app.get("/")
def home():
    return {"message": "Welcome to PoshanGuide. Open /docs to try the API."}


@app.get("/health")
def health():
    return {"status": "ok", "data_entries": len(DATA)}


@app.get("/ask")
def ask(question: str):
    """Answer from our own data, or say we cannot answer."""
    answer = find_answer(question)
    if answer is None:
        return {
            "question": question,
            "answered": False,
            "answer": "Sorry, I can't answer this from my data.",
        }
    return {"question": question, "answered": True, "answer": answer}
