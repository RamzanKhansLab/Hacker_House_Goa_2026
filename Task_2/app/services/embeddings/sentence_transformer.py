from __future__ import annotations

from typing import Any, cast

from app.core.errors import ConfigurationError
from app.services.embeddings.base import EmbeddingProvider


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Optional multilingual semantic provider loaded once at application startup."""

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ConfigurationError(
                "sentence-transformers is required for EMBEDDING_BACKEND=sentence_transformer; install .[ml]"
            ) from exc
        self._model: Any = SentenceTransformer(model_name)
        self._dimension = int(self._model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return cast(list[list[float]], self._model.encode(texts, normalize_embeddings=True).tolist())
