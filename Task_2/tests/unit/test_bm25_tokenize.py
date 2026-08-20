from app.services.retrieval.bm25 import tokenize


def test_devanagari_word_keeps_vowel_signs_and_virama() -> None:
    assert tokenize("दिल्ली भारत की राजधानी है")[:2] == ["दिल्ली", "भारत"]


def test_mixed_script_terms_remain_searchable() -> None:
    assert tokenize("RAG और retrieval") == ["rag", "और", "retrieval"]
