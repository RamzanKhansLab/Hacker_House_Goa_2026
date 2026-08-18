from __future__ import annotations

import json
import math
from pathlib import Path

from app.services.retrieval.base import VectorStore
from app.services.types import Chunk, SearchHit


class LocalVectorStore(VectorStore):
    """Portable exact cosine index for development, tests, and small deployments."""

    def __init__(self) -> None:
        self._entries: list[tuple[Chunk, list[float]]] = []

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have equal lengths")
        existing = {chunk.chunk_id: index for index, (chunk, _) in enumerate(self._entries)}
        for chunk, vector in zip(chunks, vectors, strict=True):
            if chunk.chunk_id in existing:
                self._entries[existing[chunk.chunk_id]] = (chunk, vector)
            else:
                self._entries.append((chunk, vector))

    def search(
        self, vector: list[float], limit: int, language: str | None = None, cross_language: bool = False
    ) -> list[SearchHit]:
        scored: list[SearchHit] = []
        candidates = self._entries
        language_matches = [entry for entry in candidates if language and entry[0].language == language]
        if language_matches and not cross_language:
            candidates = language_matches
        for chunk, candidate in candidates:
            score = max(0.0, _cosine(vector, candidate))
            scored.append(SearchHit(chunk=chunk, score=score, dense_score=score))
        return sorted(scored, key=lambda hit: hit.score, reverse=True)[:limit]

    def count(self) -> int:
        return len(self._entries)

    def health(self) -> bool:
        return bool(self._entries)

    def save(self, path: Path, manifest: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "manifest": manifest,
            "entries": [{"chunk": chunk.as_dict(), "vector": vector} for chunk, vector in self._entries],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> tuple[LocalVectorStore, dict[str, object]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        store = cls()
        store._entries = [
            (Chunk.from_dict(entry["chunk"]), [float(value) for value in entry["vector"]])
            for entry in payload["entries"]
        ]
        return store, dict(payload.get("manifest", {}))


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)
