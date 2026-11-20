"""Records: document chunks must keep source, page and title (Day 07 records)."""
import json

from app.chunking import chunk_documents, chunk_text, load_documents


def test_every_chunk_keeps_source_page_and_title(docs_dir):
    chunks = chunk_documents(docs_dir)
    assert chunks
    for c in chunks:
        assert c.source.endswith(".md")
        assert c.page >= 1
        assert c.title
        assert c.text.strip()


def test_page_numbers_follow_page_markers(docs_dir):
    pages = {(c.source, c.page) for c in chunk_documents(docs_dir)}
    assert ("iron.md", 1) in pages
    assert ("iron.md", 2) in pages
    assert ("milk.md", 1) in pages


def test_title_comes_from_first_heading(docs_dir):
    titles = {c.source: c.title for c in chunk_documents(docs_dir)}
    assert titles["iron.md"] == "Iron Guide"
    assert titles["milk.md"] == "Milk Guide"


def test_chunk_ids_are_unique(docs_dir):
    ids = [c.id for c in chunk_documents(docs_dir)]
    assert len(ids) == len(set(ids))


def test_long_text_is_split_and_nothing_is_lost():
    text = " ".join(f"Sentence number {i} about nutrition." for i in range(80))
    chunks = chunk_text(text, max_chars=300, overlap=40)
    assert len(chunks) > 1
    assert "Sentence number 0 " in chunks[0]
    assert "Sentence number 79 " in chunks[-1]


def test_empty_folder_gives_no_chunks(tmp_path):
    assert chunk_documents(tmp_path) == []


def test_json_entries_become_pages(tmp_path):
    entries = [{"keywords": ["iron"], "answer": "Eat dal."}, {"keywords": ["milk"], "answer": "Drink milk."}]
    (tmp_path / "foods.json").write_text(json.dumps(entries), encoding="utf-8")
    docs = load_documents(tmp_path)
    assert [d["page"] for d in docs] == [1, 2]
    assert docs[0]["text"].startswith("iron")
