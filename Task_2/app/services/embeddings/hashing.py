from __future__ import annotations

import hashlib
import math
import re

from app.services.embeddings.base import EmbeddingProvider

_TOKEN_RE = re.compile(r"[\w\u0900-\u0d7f]+", re.UNICODE)


class HashingEmbeddingProvider(EmbeddingProvider):
    """Deterministic multilingual-friendly character/token hashing fallback.

    It keeps the demo and tests self-contained. Production should select the
    sentence-transformer provider through `EMBEDDING_BACKEND=sentence_transformer`.
    """

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        normalized = " ".join(text.lower().split())
        tokens = _TOKEN_RE.findall(normalized)
        features = tokens + [normalized[index : index + 3] for index in range(max(0, len(normalized) - 2))]
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[bucket] += sign
        magnitude = math.sqrt(sum(value * value for value in vector))
        return [value / magnitude for value in vector] if magnitude else vector
