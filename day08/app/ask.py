"""POST /ask - answer from the documents with citations (Day 08)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm import LLMError
from app.rag import TOP_K, answer_question

router = APIRouter(tags=["ask"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Which foods are rich in iron for a 2-year-old?"])
    top_k: int = Field(TOP_K, ge=1, le=10, description="How many chunks to retrieve")


class Citation(BaseModel):
    id: int
    source: str
    page: int
    title: str
    score: float
    snippet: str


class AskResponse(BaseModel):
    question: str
    answer: str
    answerable: bool
    citations: list[Citation]


@router.post("/ask", response_model=AskResponse)
def ask_documents(req: AskRequest):
    """Answer from the PoshanGuide documents. Says "I don't know" when they do not contain the answer."""
    try:
        return answer_question(req.question, top_k=req.top_k)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"Model did not return valid JSON: {exc}")
