"""RAG rules that do not need the web server: citations are required, otherwise 'I don't know'."""
from app.rag import IDK_ANSWER, answer_question


def test_answer_without_any_citation_becomes_i_dont_know(fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm({"answerable": True, "answer": "Ragi is good.", "sources": []})
    result = answer_question("Which foods are rich in iron?")
    assert result["answerable"] is False
    assert result["answer"] == IDK_ANSWER
    assert result["citations"] == []


def test_citation_numbers_are_read_from_the_answer_text(fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm({"answerable": True, "answer": "Ragi is good [1].", "sources": []})
    result = answer_question("Which foods are rich in iron?")
    assert result["answerable"] is True
    assert result["citations"][0]["id"] == 1


def test_invalid_source_number_becomes_i_dont_know(fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm({"answerable": True, "answer": "Something [9].", "sources": [9]})
    assert answer_question("Which foods are rich in iron?")["answerable"] is False


def test_model_that_says_i_dont_know_is_respected(fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm({"answerable": True, "answer": "I don't know", "sources": [1]})
    result = answer_question("Which foods are rich in iron?")
    assert result["answer"].startswith("I don't know")
    assert result["citations"] == []


def test_config_is_reported_back(fake_retrieval, fake_llm, hit):
    fake_retrieval([hit()])
    fake_llm({"answerable": True, "answer": "Ragi [1].", "sources": [1]})
    result = answer_question("Which foods are rich in iron?", top_k=3, max_chars=400)
    assert result["config"] == {"top_k": 3, "chunk_size": 400}
