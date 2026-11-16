"""GET /search/semantic?q=...  (Day 07)"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.vectorstore import index_all, semantic_search

router = APIRouter(prefix="/search", tags=["search"])


class Hit(BaseModel):
    rank: int
    score: float
    text: str
    source: str
    page: int
    title: str
    chunk_id: str


class SearchResponse(BaseModel):
    q: str
    k: int
    count: int
    hits: list[Hit]


@router.get("/semantic", response_model=SearchResponse)
def semantic(
    q: str = Query(..., min_length=2, description="Your question, e.g. iron rich foods for toddlers"),
    k: int = Query(5, ge=1, le=20, description="How many chunks to return"),
):
    """Find the document chunks closest in meaning to the question."""
    try:
        hits = semantic_search(q, k)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"q": q, "k": k, "count": len(hits), "hits": hits}


@router.post("/reindex")
def reindex():
    """Rebuild the Chroma index from everything in documents/."""
    try:
        return index_all(reset=True)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
