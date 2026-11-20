"""Turn text into embeddings (Day 07).

Uses Chroma's built-in model all-MiniLM-L6-v2 (ONNX). It runs on your own computer,
needs no API key, and downloads about 80 MB the first time it is used.
"""
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

EMBED_MODEL = "all-MiniLM-L6-v2 (Chroma default, local)"

_ef = None


def _get_ef():
    global _ef
    if _ef is None:
        _ef = DefaultEmbeddingFunction()
    return _ef


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """Embed many texts. Returns one list of floats per text."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vectors.extend([[float(x) for x in v] for v in _get_ef()(batch)])
    return vectors


def embed_query(query: str) -> list[float]:
    """Embed one search question."""
    return embed_texts([query])[0]
