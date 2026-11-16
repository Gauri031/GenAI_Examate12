"""Day 09 / S1 - hand-written agent loop (no framework): think -> call tool -> observe -> repeat."""
import json
from pathlib import Path
from typing import Optional

from app.llm import decide
from app.tools import TOOL_SPECS, daily_sugar_salt_counter

MAX_STEPS = 5
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ---- RAG search: plug in YOUR existing search here -------------------------
try:
    from app.rag import search as _rag_search   # <-- change to your real module/function
except ImportError:
    _rag_search = None


def rag_search(query: str, k: int = 3) -> dict:
    if _rag_search is not None:
        hits = _rag_search(query)
        return {"results": [h if isinstance(h, str) else str(h) for h in hits][:k]}
    # fallback: naive keyword search over data/*.txt so the demo runs standalone
    words = {w for w in query.lower().split() if len(w) > 3}
    scored = []
    for p in DATA_DIR.glob("*.txt"):
        for para in p.read_text(encoding="utf-8").split("\n\n"):
            score = sum(w in para.lower() for w in words)
            if score:
                scored.append((score, para.strip()))
    scored.sort(reverse=True)
    return {"results": [t for _, t in scored[:k]] or ["No guideline passages found."]}


def run_tool(name: str, tool_input: dict) -> dict:
    if name == "daily_sugar_salt_counter":
        return daily_sugar_salt_counter(**tool_input)
    if name == "rag_search":
        return rag_search(**tool_input)
    return {"error": f"unknown tool {name}"}


def run_agent(question: str, items: Optional[list] = None) -> dict:
    content = question + (f"\nITEMS: {json.dumps(items)}" if items else "")
    messages = [{"role": "user", "content": content}]
    trace = []
    for _ in range(MAX_STEPS):
        d = decide(messages, TOOL_SPECS)
        if "final" in d:
            return {"answer": d["final"], "trace": trace}
        obs = run_tool(d["action"], d.get("input", {}))
        trace.append({"tool": d["action"], "input": d.get("input"), "observation": obs})
        messages.append({"role": "assistant", "content": json.dumps(d)})
        messages.append({"role": "tool", "content": json.dumps(obs)})
    return {"answer": "Stopped: step limit reached.", "trace": trace}


if __name__ == "__main__":
    demo = [{"name": "cola can", "servings": 2}, {"name": "instant noodles", "servings": 1}]
    print(json.dumps(run_agent("Check my day", demo), indent=2))
