"""POST /agent"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph import is_waiting, resume_turn, start_turn

router = APIRouter()


class AgentRequest(BaseModel):
    thread_id: str = "default"
    message: Optional[str] = None      # new user message
    items: Optional[list] = None       # [{"name": "cola can", "servings": 2}]
    approve: Optional[bool] = None     # answer to a pending approval


@router.post("/agent")
def agent(req: AgentRequest):
    if req.approve is not None:
        if not is_waiting(req.thread_id):
            raise HTTPException(400, "Nothing waiting for approval on this thread_id.")
        return resume_turn(req.thread_id, req.approve)
    if not req.message:
        raise HTTPException(400, "Send 'message' (or 'approve' to answer a pending approval).")
    if is_waiting(req.thread_id):
        raise HTTPException(409, "This thread is waiting for approval. Send {'approve': true/false}.")
    return start_turn(req.thread_id, req.message, req.items)
