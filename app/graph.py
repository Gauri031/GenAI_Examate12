"""Day 09 / S2 - the same agent rebuilt in LangGraph: memory (checkpointer) + ONE approval step."""
import json
import operator
from typing import Annotated, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent_loop import MAX_STEPS, run_tool
from app.llm import decide
from app.tools import TOOL_SPECS

APPROVAL_TOOLS = {"daily_sugar_salt_counter"}   # the one step that needs a human OK


class State(TypedDict):
    messages: Annotated[list, operator.add]   # memory: grows across turns of the same thread_id
    pending: Optional[dict]
    answer: Optional[str]
    steps: int


def plan(state: State):
    if state["steps"] >= MAX_STEPS:
        msg = "Stopped: step limit reached."
        return {"messages": [{"role": "assistant", "content": msg}], "pending": None, "answer": msg}
    d = decide(state["messages"], TOOL_SPECS)
    if "final" in d:
        return {"messages": [{"role": "assistant", "content": d["final"]}], "pending": None, "answer": d["final"]}
    return {"pending": d, "steps": state["steps"] + 1}


def approve(state: State):
    decision = interrupt({"tool": state["pending"]["action"], "input": state["pending"].get("input")})
    if decision.get("approved"):
        return {}
    return {"pending": None,
            "messages": [{"role": "tool", "content": json.dumps({"error": "User rejected the tool call."})}]}


def act(state: State):
    d = state["pending"]
    obs = run_tool(d["action"], d.get("input", {}))
    return {"pending": None,
            "messages": [{"role": "assistant", "content": json.dumps(d)},
                         {"role": "tool", "content": json.dumps(obs)}]}


def after_plan(state: State):
    p = state["pending"]
    if p is None:
        return END
    return "approve" if p["action"] in APPROVAL_TOOLS else "act"


def after_approve(state: State):
    return "act" if state["pending"] else "plan"


def build_graph():
    g = StateGraph(State)
    g.add_node("plan", plan)
    g.add_node("approve", approve)
    g.add_node("act", act)
    g.add_edge(START, "plan")
    g.add_conditional_edges("plan", after_plan, {"approve": "approve", "act": "act", END: END})
    g.add_conditional_edges("approve", after_approve, {"act": "act", "plan": "plan"})
    g.add_edge("act", "plan")
    return g.compile(checkpointer=MemorySaver())


graph = build_graph()


def _result(config, out):
    snap = graph.get_state(config)
    if snap.next:   # paused at the approval step
        pending = out["__interrupt__"][0].value if "__interrupt__" in out else None
        return {"status": "needs_approval", "pending": pending}
    return {"status": "done", "answer": out.get("answer")}


def start_turn(thread_id: str, message: str, items: Optional[list] = None) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    content = message + (f"\nITEMS: {json.dumps(items)}" if items else "")
    out = graph.invoke({"messages": [{"role": "user", "content": content}],
                        "pending": None, "answer": None, "steps": 0}, config)
    return _result(config, out)


def resume_turn(thread_id: str, approved: bool) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    out = graph.invoke(Command(resume={"approved": approved}), config)
    return _result(config, out)


def is_waiting(thread_id: str) -> bool:
    return bool(graph.get_state({"configurable": {"thread_id": thread_id}}).next)
