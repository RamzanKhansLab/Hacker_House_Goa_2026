from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.types import Chunk, SearchHit


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    @abstractmethod
    def search(
        self, vector: list[float], limit: int, language: str | None = None, cross_language: bool = False
    ) -> list[SearchHit]: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def health(self) -> bool: ...
