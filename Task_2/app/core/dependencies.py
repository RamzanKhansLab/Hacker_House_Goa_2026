from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

from app.config import Settings
from app.pipeline.orchestrator import RAGOrchestrator
from app.services.context import ContextBuilder
from app.services.embeddings import HashingEmbeddingProvider, SentenceTransformerEmbeddingProvider
from app.services.embeddings.base import EmbeddingProvider
from app.services.grounding.validator import GroundingValidator
from app.services.guardrails.analyzer import QueryAnalyzer
from app.services.llm import MockLLMProvider, OpenAICompatibleProvider
from app.services.llm.base import LLMProvider
from app.services.reranking.lexical import LexicalReranker
from app.services.retrieval import LocalVectorStore, QdrantVectorStore, RetrievalEngine
from app.services.retrieval.base import VectorStore
from app.services.stt import (
    MockSpeechToTextProvider,
    SarvamSpeechToTextProvider,
    SpeechToTextProvider,
)
from app.services.types import Chunk


class RateLimiter:
    """Small in-process limiter suitable for one free-tier instance."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, key: str) -> bool:
        now = time.monotonic()
        entries = self._requests[key]
        while entries and now - entries[0] >= 60:
            entries.popleft()
        if len(entries) >= self.limit:
            return False
        entries.append(now)
        return True


@dataclass
class ApplicationServices:
    settings: Settings
    store: VectorStore
    stt: SpeechToTextProvider
    orchestrator: RAGOrchestrator
    manifest: dict[str, object]
    rate_limiter: RateLimiter

    async def close(self) -> None:
        for provider in (self.stt, self.orchestrator.llm):
            close = getattr(provider, "close", None)
            if close:
                await close()


def _create_embedder(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_backend == "hash":
        return HashingEmbeddingProvider()
    if settings.embedding_backend == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider(settings.embedding_model)
    raise ValueError(f"Unsupported EMBEDDING_BACKEND: {settings.embedding_backend}")


def _load_local_index(settings: Settings, embedder: EmbeddingProvider) -> tuple[VectorStore, list[Chunk], dict[str, object]]:
    if settings.index_path.exists():
        store, manifest = LocalVectorStore.load(settings.index_path)
        return store, [chunk for chunk, _ in store._entries], manifest
    if not settings.demo_mode:
        return LocalVectorStore(), [], {"error": f"Index not found: {settings.index_path}"}
    from app.services.chunking import chunk_records
    from ingestion.io import read_jsonl

    records = read_jsonl(Path("data/demo/documents.jsonl"))
    chunks = chunk_records(records, "semantic")
    store = LocalVectorStore()
    store.upsert(chunks, embedder.embed([chunk.text for chunk in chunks]))
    return store, chunks, {"dataset": "bundled demo subset", "document_count": len(records), "chunk_count": len(chunks)}


def create_services(settings: Settings) -> ApplicationServices:
    embedder = _create_embedder(settings)
    if settings.vector_store == "qdrant":
        store: VectorStore = QdrantVectorStore(
            settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_collection, settings.vector_db_timeout_seconds
        )
        chunks: list[Chunk] = []
        manifest: dict[str, object] = {"backend": "qdrant", "collection": settings.qdrant_collection}
    elif settings.vector_store == "local":
        store, chunks, manifest = _load_local_index(settings, embedder)
    else:
        raise ValueError(f"Unsupported VECTOR_STORE: {settings.vector_store}")
    stt: SpeechToTextProvider = MockSpeechToTextProvider() if settings.demo_mode else SarvamSpeechToTextProvider(
        settings.sarvam_api_key, settings.sarvam_base_url, settings.sarvam_stt_model, settings.sarvam_stt_mode, settings.stt_timeout_seconds
    )
    llm: LLMProvider = MockLLMProvider() if settings.demo_mode or settings.llm_provider == "mock" else OpenAICompatibleProvider(
        settings.llm_base_url, settings.llm_api_key, settings.llm_model, settings.llm_timeout_seconds
    )
    orchestrator = RAGOrchestrator(
        settings,
        RetrievalEngine(store, embedder, chunks, settings.rrf_k),
        QueryAnalyzer(),
        LexicalReranker(),
        ContextBuilder(settings.max_context_tokens),
        llm,
        GroundingValidator(settings.grounding_threshold),
    )
    return ApplicationServices(settings, store, stt, orchestrator, manifest, RateLimiter(settings.rate_limit_per_minute))
