"""PoshanGuide - main FastAPI app (Day 07).

Endpoints
  GET  /                  welcome message
  GET  /health            health check
  GET  /ask               answer from our own keyword data (Day 05)
  POST /chat              LLM answer: answer / confidence / follow_up (Day 06)
  GET  /search/semantic   semantic search over document chunks (Day 07)
  POST /search/reindex    rebuild the Chroma index (Day 07)

Run from the day07 folder:  uvicorn app.main:app --reload
"""
import json
from pathlib import Path

from fastapi import FastAPI

from app.chat import router as chat_router
from app.search import router as search_router

app = FastAPI(
    title="PoshanGuide",
    description="Nutrition guidance for families: keyword data, LLM chat and semantic search.",
)
app.include_router(chat_router)
app.include_router(search_router)

ROOT = Path(__file__).resolve().parent.parent
DATA_CANDIDATES = [
    ROOT / "data" / "nutrition.json",
    ROOT.parent / "day06" / "data" / "nutrition.json",
    ROOT.parent / "day02" / "data" / "nutrition.json",
]


def load_data() -> list[dict]:
    for path in DATA_CANDIDATES:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return []


DATA = load_data()


def find_answer(question: str) -> str | None:
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
    """Answer from our own keyword data, or say we cannot answer."""
    answer = find_answer(question)
    if answer is None:
        return {"question": question, "answered": False,
                "answer": "Sorry, I can't answer this from my data."}
    return {"question": question, "answered": True, "answer": answer}
