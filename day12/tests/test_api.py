"""API: /health and POST /ask (with a fake LLM)."""
from app.llm import LLMError


def test_health_is_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert isinstance(body["data_entries"], int)


def test_ask_answers_with_citations(client, fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    llm = fake_llm({"answerable": True, "answer": "Give ragi and dal [1].", "sources": [1]})
    r = client.post("/ask", json={"question": "Which foods are rich in iron for a 2-year-old?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answerable"] is True
    assert "ragi" in body["answer"]
    assert body["citations"][0]["source"] == "child_nutrition.md"
    assert body["citations"][0]["page"] == 1
    assert len(llm.calls) == 1
    assert "[1] (source: child_nutrition.md" in llm.calls[0]["user"]   # the chunk was given to the model


def test_ask_says_i_dont_know_for_q6(client, fake_retrieval, fake_llm, hit):
    fake_retrieval([hit(source="common_foods.md", score=0.45, text="This document has no information on nutritionists.")])
    fake_llm({"answerable": False, "answer": "I don't know", "sources": []})
    r = client.post("/ask", json={"question": "Which nutritionist near my village is free this week?"})
    body = r.json()
    assert r.status_code == 200
    assert body["answerable"] is False
    assert body["answer"].startswith("I don't know")
    assert body["citations"] == []


def test_ask_skips_the_llm_when_nothing_is_close(client, fake_retrieval, fake_llm, hit):
    fake_retrieval([hit(score=0.05)])
    llm = fake_llm({"answerable": True, "answer": "Should never be used [1].", "sources": [1]})
    r = client.post("/ask", json={"question": "What is the weather today?"})
    assert r.json()["answer"].startswith("I don't know")
    assert llm.calls == []


def test_ask_rejects_a_too_short_question(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 422


def test_ask_returns_502_when_the_llm_fails(client, fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm(LLMError("GROQ_API_KEY is missing"))
    r = client.post("/ask", json={"question": "Which foods are rich in iron?"})
    assert r.status_code == 502
    assert "GROQ_API_KEY" in r.json()["detail"]


def test_ask_returns_502_when_the_llm_returns_bad_json(client, fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm("this is not json")
    r = client.post("/ask", json={"question": "Which foods are rich in iron?"})
    assert r.status_code == 502
