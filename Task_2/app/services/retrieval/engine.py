from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from app.services.embeddings.base import EmbeddingProvider
from app.services.retrieval.base import VectorStore
from app.services.retrieval.bm25 import BM25Index
from app.services.retrieval.fusion import reciprocal_rank_fusion
from app.services.types import Chunk, SearchHit


@dataclass(frozen=True)
class RetrievalResult:
    dense: list[SearchHit]
    lexical: list[SearchHit]
    fused: list[SearchHit]
    embedding_ms: float
    dense_ms: float
    lexical_ms: float
    fusion_ms: float


class RetrievalEngine:
    """Runs dense and lexical paths concurrently, then applies RRF."""

    def __init__(self, store: VectorStore, embedder: EmbeddingProvider, chunks: list[Chunk], rrf_k: int = 60) -> None:
        self.store = store
        self.embedder = embedder
        self.bm25 = BM25Index(chunks)
        self.rrf_k = rrf_k

    async def retrieve(
        self, query: str, limit: int, language: str | None, cross_language: bool
    ) -> RetrievalResult:
        start = time.perf_counter()
        vector = await asyncio.to_thread(self.embedder.embed_query, query)
        embedding_ms = (time.perf_counter() - start) * 1000

        async def dense_path() -> tuple[list[SearchHit], float]:
            stage_start = time.perf_counter()
            hits = await asyncio.to_thread(self.store.search, vector, limit, language, cross_language)
            return hits, (time.perf_counter() - stage_start) * 1000

        async def lexical_path() -> tuple[list[SearchHit], float]:
            stage_start = time.perf_counter()
            hits = await asyncio.to_thread(self.bm25.search, query, limit, language, cross_language)
            return hits, (time.perf_counter() - stage_start) * 1000

        (dense, dense_ms), (lexical, lexical_ms) = await asyncio.gather(dense_path(), lexical_path())
        fusion_start = time.perf_counter()
        fused = reciprocal_rank_fusion([dense, lexical], limit, self.rrf_k)
        return RetrievalResult(
            dense=dense,
            lexical=lexical,
            fused=fused,
            embedding_ms=embedding_ms,
            dense_ms=dense_ms,
            lexical_ms=lexical_ms,
            fusion_ms=(time.perf_counter() - fusion_start) * 1000,
        )
