from __future__ import annotations

import asyncio
import time
import uuid
from collections import OrderedDict

from app.config import Settings
from app.schemas.models import AnswerResponse, LatencyBreakdown, SourceReference
from app.services.context import ContextBuilder
from app.services.grounding.validator import GroundingValidator
from app.services.guardrails.analyzer import QueryAnalyzer
from app.services.llm.base import LLMProvider
from app.services.reranking.lexical import LexicalReranker
from app.services.retrieval.engine import RetrievalEngine
from app.services.types import SearchHit

_INSUFFICIENT = "I don't have enough information in the provided knowledge base to answer that."
_UNSAFE = "I can't help with that request."


class RAGOrchestrator:
    def __init__(
        self,
        settings: Settings,
        retrieval: RetrievalEngine,
        analyzer: QueryAnalyzer,
        reranker: LexicalReranker,
        context_builder: ContextBuilder,
        llm: LLMProvider,
        grounding: GroundingValidator,
    ) -> None:
        self.settings = settings
        self.retrieval = retrieval
        self.analyzer = analyzer
        self.reranker = reranker
        self.context_builder = context_builder
        self.llm = llm
        self.grounding = grounding
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        self.cache: OrderedDict[str, AnswerResponse] = OrderedDict()

    async def answer(
        self, query: str, language: str | None = None, cross_language: bool = False, transcript: str | None = None
    ) -> AnswerResponse:
        cache_key = f"{query}|{language or ''}|{cross_language}"
        if self.settings.query_cache_size and transcript is None and cache_key in self.cache:
            cached = self.cache.pop(cache_key)
            self.cache[cache_key] = cached
            return cached.model_copy(update={"request_id": str(uuid.uuid4())})
        async with self.semaphore:
            response = await self._answer(query, language, cross_language, transcript)
        if self.settings.query_cache_size and transcript is None and response.guardrail_status == "PASS":
            self.cache[cache_key] = response
            while len(self.cache) > self.settings.query_cache_size:
                self.cache.popitem(last=False)
        return response

    async def _answer(
        self, query: str, language: str | None, cross_language: bool, transcript: str | None
    ) -> AnswerResponse:
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        latency = LatencyBreakdown()
        preprocessing_start = time.perf_counter()
        analysis = self.analyzer.analyze(query[: self.settings.max_query_chars], language)
        latency.preprocessing_ms = (time.perf_counter() - preprocessing_start) * 1000
        if analysis.classification in {"UNSAFE", "INJECTION_BLOCKED", "AMBIGUOUS"}:
            status = "UNSAFE" if analysis.classification == "UNSAFE" else (
                "INJECTION_BLOCKED" if analysis.classification == "INJECTION_BLOCKED" else "INSUFFICIENT_CONTEXT"
            )
            answer = _UNSAFE if status == "UNSAFE" else _INSUFFICIENT
            return self._response(
                request_id, query, transcript, analysis.language, answer, [], False, 0.0, status, latency, start
            )

        retrieval_result = await self.retrieval.retrieve(
            analysis.normalized_query, self.settings.retrieve_top_k, analysis.language, cross_language
        )
        latency.embedding_ms = retrieval_result.embedding_ms
        latency.dense_retrieval_ms = retrieval_result.dense_ms
        latency.lexical_retrieval_ms = retrieval_result.lexical_ms
        latency.fusion_ms = retrieval_result.fusion_ms
        candidates = retrieval_result.fused
        evidence_score = max(
            (max(hit.lexical_score / (hit.lexical_score + 1), hit.dense_score) for hit in candidates), default=0.0
        )
        if not candidates or evidence_score < self.settings.min_retrieval_score:
            return self._response(
                request_id,
                query,
                transcript,
                analysis.language,
                _INSUFFICIENT,
                [],
                False,
                0.0,
                "INSUFFICIENT_CONTEXT",
                latency,
                start,
            )

        rerank_start = time.perf_counter()
        final_hits = (
            self.reranker.rerank(analysis.normalized_query, candidates, self.settings.rerank_top_k)
            if self.settings.reranker_enabled
            else candidates[: self.settings.rerank_top_k]
        )
        latency.reranking_ms = (time.perf_counter() - rerank_start) * 1000
        context_start = time.perf_counter()
        context, selected = self.context_builder.build(final_hits)
        latency.context_ms = (time.perf_counter() - context_start) * 1000
        if not context:
            return self._response(
                request_id, query, transcript, analysis.language, _INSUFFICIENT, [], False, 0.0,
                "INSUFFICIENT_CONTEXT", latency, start
            )

        llm_start = time.perf_counter()
        answer = await self.llm.generate(analysis.normalized_query, context, analysis.language)
        latency.llm_ms = (time.perf_counter() - llm_start) * 1000
        grounding_start = time.perf_counter()
        grounding = self.grounding.validate(answer, context)
        latency.grounding_ms = (time.perf_counter() - grounding_start) * 1000
        if not grounding.grounded:
            return self._response(
                request_id, query, transcript, analysis.language, _INSUFFICIENT, selected, False, 0.0,
                "INSUFFICIENT_CONTEXT", latency, start
            )
        return self._response(
            request_id,
            query,
            transcript,
            analysis.language,
            answer,
            selected,
            True,
            min(1.0, 0.55 * evidence_score + 0.45 * grounding.support_score),
            "PASS",
            latency,
            start,
        )

    def _response(
        self,
        request_id: str,
        query: str,
        transcript: str | None,
        language: str,
        answer: str,
        hits: list[SearchHit],
        grounded: bool,
        confidence: float,
        status: str,
        latency: LatencyBreakdown,
        start: float,
    ) -> AnswerResponse:
        latency.rag_total_ms = (time.perf_counter() - start) * 1000
        latency.end_to_end_ms = latency.rag_total_ms + latency.stt_ms
        sources = [
            SourceReference(
                chunk_id=hit.chunk.chunk_id,
                document_id=hit.chunk.document_id,
                language=hit.chunk.language,
                score=round(hit.score, 4),
                snippet=hit.chunk.text[:280],
                title=hit.chunk.title,
            )
            for hit in hits
        ]
        return AnswerResponse(
            request_id=request_id,
            query=query,
            transcript=transcript,
            language=language,
            answer=answer,
            sources=sources,
            grounded=grounded,
            confidence=confidence,
            guardrail_status=status,  # type: ignore[arg-type]
            latency=latency,
            demo_mode=self.settings.demo_mode,
        )
