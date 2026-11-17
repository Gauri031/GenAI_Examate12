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

    required = ("answer", "confidence", "follow_up")
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"Model response is missing required fields: {', '.join(missing)}")
    if not all(isinstance(data[field], str) for field in required):
        raise ValueError("Model response fields must all be strings.")

    confidence = data["confidence"].lower()
    if confidence not in {"high", "medium", "low"}:
        raise ValueError("Model confidence must be high, medium, or low.")
    answer = data["answer"].strip()
    follow_up = data["follow_up"].strip()
    if not answer or not follow_up:
        raise ValueError("Model answer and follow_up must not be empty.")
    return {
        "answer": answer,
        "confidence": confidence,
        "follow_up": follow_up,
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
