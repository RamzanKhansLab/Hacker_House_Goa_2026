from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import Settings
from app.core.errors import ConfigurationError
from app.core.rate_limit import InMemoryRateLimiter
from app.pipeline.orchestrator import RAGOrchestrator
from app.services.chunking import chunk_records
from app.services.context import ContextBuilder
from app.services.embeddings import HashingEmbeddingProvider, SentenceTransformerEmbeddingProvider
from app.services.embeddings.base import EmbeddingProvider
from app.services.grounding import GroundingValidator
from app.services.guardrails import QueryAnalyzer
from app.services.llm import MockLLMProvider, OpenAICompatibleProvider
from app.services.llm.base import LLMProvider
from app.services.reranking import LexicalReranker
from app.services.retrieval import LocalVectorStore, QdrantVectorStore, RetrievalEngine
from app.services.retrieval.base import VectorStore
from app.services.stt import MockSpeechToTextProvider, SarvamSpeechToTextProvider, SpeechToTextProvider
from app.services.types import Chunk


class ApplicationServices:
    def __init__(
        self,
        settings: Settings,
        orchestrator: RAGOrchestrator,
        stt: SpeechToTextProvider,
        store: VectorStore,
        manifest: dict[str, object],
    ) -> None:
        self.settings = settings
        self.orchestrator = orchestrator
        self.stt = stt
        self.store = store
        self.manifest = manifest
        self.rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)

    async def close(self) -> None:
        await self.stt.close()
        close = getattr(self.orchestrator.llm, "close", None)
        if close:
            result = close()
            if hasattr(result, "__await__"):
                await result


def create_services(settings: Settings) -> ApplicationServices:
    embedder = _create_embedder(settings)
    chunks, local_store, manifest = _load_local_index(settings, embedder)
    store: VectorStore
    if settings.vector_store == "qdrant":
        store = QdrantVectorStore(
            settings.qdrant_url,
            settings.qdrant_api_key,
            settings.qdrant_collection,
            settings.vector_db_timeout_seconds,
        )
    elif settings.vector_store == "local":
        store = local_store
    else:
        raise ConfigurationError("VECTOR_STORE must be local or qdrant")
    retrieval = RetrievalEngine(store, embedder, chunks)
    llm = _create_llm(settings)
    stt = _create_stt(settings)
    orchestrator = RAGOrchestrator(
        settings=settings,
        retrieval=retrieval,
        analyzer=QueryAnalyzer(),
        reranker=LexicalReranker(),
        context_builder=ContextBuilder(settings.max_context_tokens),
        llm=llm,
        grounding=GroundingValidator(),
    )
    return ApplicationServices(settings, orchestrator, stt, store, manifest)


def _create_embedder(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_backend == "hash":
        return HashingEmbeddingProvider()
    if settings.embedding_backend == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider(settings.embedding_model)
    raise ConfigurationError("EMBEDDING_BACKEND must be hash or sentence_transformer")


def _load_local_index(settings: Settings, embedder: EmbeddingProvider) -> tuple[list[Chunk], LocalVectorStore, dict[str, object]]:
    if settings.index_path.exists():
        store, manifest = LocalVectorStore.load(settings.index_path)
        chunks = [chunk for chunk, _ in store._entries]  # Local index owns persisted vectors.
        return chunks, store, manifest
    records = _read_jsonl(Path("data/demo/documents.jsonl"))
    chunks = chunk_records(records, "semantic")
    store = LocalVectorStore()
    store.upsert(chunks, embedder.embed([chunk.text for chunk in chunks]))
    return chunks, store, {
        "dataset": "bundled demo subset; run python -m ingestion.build_index for MSMARCO-XI",
        "embedding_model": settings.embedding_model,
        "chunking_strategy": "semantic",
        "document_count": len(records),
        "chunk_count": len(chunks),
        "languages": sorted({chunk.language for chunk in chunks}),
        "mode": "demo",
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ConfigurationError(f"Required demo data is missing: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _create_llm(settings: Settings) -> LLMProvider:
    if settings.demo_mode or settings.llm_provider == "mock":
        return MockLLMProvider()
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleProvider(
            settings.llm_base_url, settings.llm_api_key, settings.llm_model, settings.llm_timeout_seconds
        )
    raise ConfigurationError("LLM_PROVIDER must be mock or openai_compatible")


def _create_stt(settings: Settings) -> SpeechToTextProvider:
    if settings.demo_mode:
        return MockSpeechToTextProvider()
    return SarvamSpeechToTextProvider(
        settings.sarvam_api_key,
        settings.sarvam_base_url,
        settings.sarvam_stt_model,
        settings.sarvam_stt_mode,
        settings.stt_timeout_seconds,
    )
