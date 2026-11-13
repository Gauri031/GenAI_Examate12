"""PoshanGuide FastAPI service. Run from day03/: uvicorn app.main:app --reload"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.config import APP_NAME, SEARCH_TOP_K
from app.records import load_records
from app.smart_search import SmartSearch

app = FastAPI(title=f"{APP_NAME} API", version="0.3")
RECORDS = load_records()
ENGINE = SmartSearch(RECORDS)
DISCLAIMER = "General nutrition information from ICMR-NIN guidelines, not medical advice."


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok", "records": len(RECORDS)}


@app.get("/records")
def list_records(limit: int = Query(10, ge=1, le=100)):
    return RECORDS[:limit]


@app.get("/records/{rec_id}")
def get_record(rec_id: int):
    for r in RECORDS:
        if r["id"] == rec_id:
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    return {"query": q, "results": ENGINE.rank(q, top_k=SEARCH_TOP_K)}


@app.post("/questions")
def ask(body: Question):
    hits = ENGINE.rank(body.question, top_k=3)
    if not hits:
        return {"answer": "No matching guideline found.", "sources": [], "disclaimer": DISCLAIMER}
    best = hits[0]
    return {
        "answer": best["key_advice"],
        "number_limit": best["number_limit"],
        "citation": f"Guideline {best['guideline_no']}, page {best['page_ref']}",
        "sources": [h["id"] for h in hits],
        "disclaimer": DISCLAIMER,
    }
