import asyncio

from app.services.embeddings import HashingEmbeddingProvider
from app.services.retrieval import LocalVectorStore, RetrievalEngine
from app.services.types import Chunk


def test_hybrid_retrieval_finds_matching_chunk() -> None:
    chunks = [
        Chunk("one", "rag", None, "RAG retrieves documents before it generates an answer.", "en"),
        Chunk("two", "other", None, "Mangroves protect tropical coastlines.", "en"),
    ]
    embedder = HashingEmbeddingProvider()
    store = LocalVectorStore()
    store.upsert(chunks, embedder.embed([chunk.text for chunk in chunks]))
    result = asyncio.run(RetrievalEngine(store, embedder, chunks).retrieve("How does RAG retrieve documents?", 2, "en", False))
    assert result.fused[0].chunk.document_id == "rag"
    assert result.lexical


def test_language_filter_falls_back_when_missing_language() -> None:
    chunk = Chunk("one", "rag", None, "RAG retrieves documents.", "en")
    embedder = HashingEmbeddingProvider()
    store = LocalVectorStore()
    store.upsert([chunk], embedder.embed([chunk.text]))
    assert store.search(embedder.embed(["RAG"])[0], 1, "hi", False)
