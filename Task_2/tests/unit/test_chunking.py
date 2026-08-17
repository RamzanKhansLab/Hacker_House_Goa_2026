from app.services.chunking import build_chunker

RECORD = {
    "id": "doc-1",
    "text": "First sentence explains RAG. Second sentence explains retrieval. Third sentence explains grounding.",
    "language": "en",
    "source_language": "eng_Latn",
    "target_language": "eng_Latn",
}


def test_all_chunking_strategies_emit_metadata() -> None:
    for name in ("fixed", "sentence", "sliding", "semantic", "metadata", "parent_child"):
        chunks = build_chunker(name).chunk(RECORD)
        assert chunks
        assert all(chunk.chunk_id and chunk.document_id == "doc-1" for chunk in chunks)
        assert all(chunk.language == "en" and chunk.token_count > 0 for chunk in chunks)


def test_parent_child_links_children() -> None:
    chunks = build_chunker("parent_child").chunk({**RECORD, "text": "word " * 120})
    assert any(chunk.parent_id for chunk in chunks)
