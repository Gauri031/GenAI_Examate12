"""Persistent Chroma index + semantic search (Day 07, extended in Day 08).

Index all chunks:   python -m app.vectorstore
The index is saved in the chroma_db/ folder, so it survives restarts.

Day 08: every chunk size gets its own collection, so two configurations can be
compared without overwriting each other.
"""
from pathlib import Path

import chromadb

from app.chunking import MAX_CHARS, chunk_documents
from app.embed import embed_query, embed_texts

ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "poshanguide"
DEFAULT_CHUNK = MAX_CHARS  # 700

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def collection_name(max_chars: int = DEFAULT_CHUNK) -> str:
    """Default chunk size -> 'poshanguide', other sizes -> 'poshanguide_c400' etc."""
    return COLLECTION_NAME if max_chars == DEFAULT_CHUNK else f"{COLLECTION_NAME}_c{max_chars}"


def get_collection(max_chars: int = DEFAULT_CHUNK):
    return get_client().get_or_create_collection(
        name=collection_name(max_chars), metadata={"hnsw:space": "cosine"}
    )


def index_all(reset: bool = True, max_chars: int = DEFAULT_CHUNK, overlap: int | None = None) -> dict:
    """Chunk every document in documents/, embed the chunks and store them in Chroma."""
    chunks = chunk_documents(max_chars=max_chars, overlap=overlap)
    if not chunks:
        raise ValueError("No chunks found. Put your documents in the 'documents/' folder.")

    name = collection_name(max_chars)
    if reset:
        try:
            get_client().delete_collection(name)
        except Exception:
            pass  # collection did not exist yet
    collection = get_collection(max_chars)

    batch = 200
    for i in range(0, len(chunks), batch):
        part = chunks[i:i + batch]
        texts = [c.text for c in part]
        collection.upsert(
            ids=[c.id for c in part],
            documents=texts,
            embeddings=embed_texts(texts),
            metadatas=[
                {"source": c.source, "page": c.page, "title": c.title, "chunk_index": c.chunk_index}
                for c in part
            ],
        )
    return {
        "documents": len({c.source for c in chunks}),
        "chunks": len(chunks),
        "chunk_size": max_chars,
        "collection": name,
        "path": str(CHROMA_DIR),
    }


def semantic_search(q: str, k: int = 5, max_chars: int = DEFAULT_CHUNK) -> list[dict]:
    """Return the k chunks closest in meaning to the question (score: higher = closer)."""
    collection = get_collection(max_chars)
    if collection.count() == 0:
        index_all(reset=False, max_chars=max_chars)  # first use: build the index automatically
    result = collection.query(
        query_embeddings=[embed_query(q)],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for rank, (cid, doc, meta, dist) in enumerate(
        zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]), 1
    ):
        hits.append(
            {
                "rank": rank,
                "score": round(1 - dist, 4),
                "text": doc,
                "source": meta["source"],
                "page": int(meta["page"]),
                "title": meta["title"],
                "chunk_id": cid,
            }
        )
    return hits


if __name__ == "__main__":
    info = index_all(reset=True)
    print(f"Indexed {info['chunks']} chunks from {info['documents']} documents into '{info['collection']}'")
    print(f"Saved at: {info['path']}")
