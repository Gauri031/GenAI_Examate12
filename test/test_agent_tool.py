"""Agent tools (app/tools.py): the functions an agent can call."""
import pytest

from app import tools


def test_search_tool_returns_compact_results(monkeypatch, hit):
    monkeypatch.setattr("app.tools.semantic_search", lambda q, k: [hit()])
    results = tools.run_tool("search_documents", query="iron", k=1)
    assert results[0]["source"] == "child_nutrition.md"
    assert set(results[0]) == {"source", "page", "title", "score", "text"}


def test_search_tool_passes_the_query_and_k(monkeypatch, hit):
    seen = {}

    def fake_search(q, k):
        seen["q"], seen["k"] = q, k
        return [hit()]

    monkeypatch.setattr("app.tools.semantic_search", fake_search)
    tools.search_documents("  iron foods  ", k=5)
    assert seen == {"q": "iron foods", "k": 5}


def test_search_tool_rejects_an_empty_query():
    with pytest.raises(ValueError):
        tools.search_documents("   ")


def test_unknown_tool_raises_key_error():
    with pytest.raises(KeyError):
        tools.run_tool("does_not_exist")


def test_nin_tool_reports_the_plate_amounts():
    amounts = tools.run_tool("nin_plate_amounts")
    assert amounts["cereals"] == 250
    assert amounts["vegetables"] == 400
    assert len(amounts) == 7
