"""Shared test helpers.

The tests never call a real LLM, never need an API key, and never need the Chroma index:
retrieval and the LLM are replaced by fakes.
"""
import json

import pytest


def make_hit(source="child_nutrition.md", page=1, score=0.62,
             text="Give dal, green leafy vegetables and ragi for iron.", title="Nutrition for Young Children"):
    """One retrieved chunk, in the same shape that semantic_search() returns."""
    return {"rank": 1, "score": score, "text": text, "source": source, "page": page,
            "title": title, "chunk_id": f"{source}-p{page}-c0"}


class FakeLLM:
    """Replaces app.rag.call_llm: returns a scripted reply and remembers every call."""

    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def __call__(self, system_prompt, user_prompt, temperature=0.0):
        self.calls.append({"system": system_prompt, "user": user_prompt})
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply if isinstance(self.reply, str) else json.dumps(self.reply)


@pytest.fixture
def hit():
    return make_hit


@pytest.fixture
def fake_retrieval(monkeypatch):
    """fake_retrieval([hit1, hit2]) makes app.rag.semantic_search return those chunks."""
    def install(hits):
        def fake_search(question, k=4, max_chars=700):
            return hits
        monkeypatch.setattr("app.rag.semantic_search", fake_search)
    return install


@pytest.fixture
def fake_llm(monkeypatch):
    """fake_llm({...}) makes app.rag.call_llm return that JSON. Returns the FakeLLM to inspect calls."""
    def install(reply):
        llm = FakeLLM(reply)
        monkeypatch.setattr("app.rag.call_llm", llm)
        return llm
    return install


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app
    return TestClient(app)


@pytest.fixture
def docs_dir(tmp_path):
    """A small documents folder: iron.md (2 pages) and milk.md (1 page)."""
    (tmp_path / "iron.md").write_text(
        "# Iron Guide\n\nEat dal, ragi and green leafy vegetables for iron.\n\n"
        "<!-- page -->\n\nAdd lemon to the meal. Vitamin C helps iron absorption.\n",
        encoding="utf-8")
    (tmp_path / "milk.md").write_text(
        "# Milk Guide\n\nCurd and buttermilk are easier to digest than milk.\n", encoding="utf-8")
    return tmp_path
