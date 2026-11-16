"""POST /chat - PoshanGuide chat endpoint (Day 06)."""
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm import LLMError, call_llm, parse_json

router = APIRouter(tags=["chat"])

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Which foods are rich in iron for a 2-year-old?"])
    prompt_version: Literal["v1", "v2"] = "v2"


class ChatResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    follow_up: str


def run_prompt(question: str, version: str = "v2") -> dict:
    """System prompt + task prompt -> LLM -> clean dict (answer, confidence, follow_up)."""
    system = load_prompt("system.md")
    task = load_prompt(f"task_{version}.md").replace("{question}", question)
    data = parse_json(call_llm(system, task))

    confidence = str(data.get("confidence", "low")).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    return {
        "answer": str(data.get("answer", "")).strip() or "Sorry, I could not produce an answer.",
        "confidence": confidence,
        "follow_up": str(data.get("follow_up", "")).strip(),
    }


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Ask PoshanGuide a nutrition question. Returns JSON: answer, confidence, follow_up."""
    try:
        return run_prompt(req.question, req.prompt_version)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"Model did not return valid JSON: {exc}")
