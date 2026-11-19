"""Search: semantic_search() formatting and GET /search/semantic."""
from app import vectorstore


class FakeCollection:
    """Looks like a Chroma collection and returns two results in Chroma's shape."""

    def __init__(self, size=3):
        self.size = size

    def count(self):
        return self.size

    def query(self, query_embeddings, n_results, include):
        if self.size == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        return {
            "ids": [["a-p1-c0", "b-p2-c0"]],
            "documents": [["text a", "text b"]],
            "metadatas": [[{"source": "a.md", "page": 1, "title": "A", "chunk_index": 0},
                           {"source": "b.md", "page": "2", "title": "B", "chunk_index": 0}]],
            "distances": [[0.2, 0.5]],
        }


def test_semantic_search_ranks_and_scores_hits(monkeypatch):
    monkeypatch.setattr(vectorstore, "get_collection", lambda max_chars=700: FakeCollection())
    monkeypatch.setattr(vectorstore, "embed_query", lambda q: [0.1, 0.2])
    hits = vectorstore.semantic_search("iron foods", k=2)
    assert [h["rank"] for h in hits] == [1, 2]
    assert hits[0]["score"] == 0.8          # score = 1 - distance
    assert hits[1]["score"] == 0.5
    assert hits[1]["page"] == 2             # page is always an int
    assert hits[0]["source"] == "a.md"


def test_semantic_search_builds_index_when_empty(monkeypatch):
    calls = []
    monkeypatch.setattr(vectorstore, "get_collection", lambda max_chars=700: FakeCollection(size=0))
    monkeypatch.setattr(vectorstore, "embed_query", lambda q: [0.1])
    monkeypatch.setattr(vectorstore, "index_all", lambda **kwargs: calls.append(kwargs))
    assert vectorstore.semantic_search("anything", k=3) == []
    assert len(calls) == 1


def test_search_endpoint_returns_hits(client, hit, monkeypatch):
    monkeypatch.setattr("app.search.semantic_search", lambda q, k: [hit(score=0.7)])
    r = client.get("/search/semantic", params={"q": "iron foods", "k": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["hits"][0]["source"] == "child_nutrition.md"
    assert body["hits"][0]["score"] == 0.7


def test_search_endpoint_validates_input(client):
    assert client.get("/search/semantic").status_code == 422                          # q is missing
    assert client.get("/search/semantic", params={"q": "iron", "k": 0}).status_code == 422   # k too small
