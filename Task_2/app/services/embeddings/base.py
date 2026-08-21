from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed stored passages; providers may specialize document prefixes."""
        return self.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed one search query; providers may specialize query prefixes."""
        return self.embed([text])[0]
