from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000, description="Typed query or STT transcript")
    language: str | None = Field(default=None, max_length=16)
    cross_language: bool = False

    @field_validator("query")
    @classmethod
    def no_blank_queries(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("query must not be blank")
        return value


class LatencyBreakdown(BaseModel):
    stt_ms: float = 0
    preprocessing_ms: float = 0
    embedding_ms: float = 0
    dense_retrieval_ms: float = 0
    lexical_retrieval_ms: float = 0
    fusion_ms: float = 0
    reranking_ms: float = 0
    context_ms: float = 0
    llm_ms: float = 0
    grounding_ms: float = 0
    rag_total_ms: float = 0
    end_to_end_ms: float = 0


class SourceReference(BaseModel):
    chunk_id: str
    document_id: str
    language: str
    score: float = Field(ge=0, le=1)
    snippet: str
    title: str | None = None


class AnswerResponse(BaseModel):
    request_id: str
    query: str
    transcript: str | None = None
    language: str
    answer: str
    sources: list[SourceReference] = []
    grounded: bool
    confidence: float = Field(ge=0, le=1)
    guardrail_status: Literal["PASS", "OFF_TOPIC", "UNSAFE", "INSUFFICIENT_CONTEXT", "INJECTION_BLOCKED"]
    latency: LatencyBreakdown
    demo_mode: bool


class TranscriptResponse(BaseModel):
    transcript: str
    language: str
    confidence: float = Field(ge=0, le=1)
    provider: str
    latency_ms: float = Field(ge=0)


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str = "goa-voice-rag"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    request_id: str | None = None
    error: str
    detail: str | None = None
