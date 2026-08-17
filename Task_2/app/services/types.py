from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    parent_id: str | None
    text: str
    language: str
    source_language: str | None = None
    target_language: str | None = None
    title: str | None = None
    strategy: str = "semantic"
    start_offset: int = 0
    end_offset: int = 0
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "parent_id": self.parent_id,
            "text": self.text,
            "language": self.language,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "title": self.title,
            "strategy": self.strategy,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "token_count": self.token_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Chunk:
        return cls(**payload)


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float
    dense_score: float = 0.0
    lexical_score: float = 0.0


@dataclass(frozen=True)
class QueryAnalysis:
    normalized_query: str
    language: str
    classification: str
    reason: str | None = None
    chunk_strategy: str = "semantic"


@dataclass(frozen=True)
class GroundingResult:
    grounded: bool
    support_score: float
    unsupported_claims: list[str]
