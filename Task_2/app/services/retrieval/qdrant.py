from __future__ import annotations

from app.core.errors import ConfigurationError, ServiceError
from app.services.retrieval.base import VectorStore
from app.services.types import Chunk, SearchHit


class QdrantVectorStore(VectorStore):
    """REST adapter. Collection creation is an explicit indexing concern."""

    def __init__(self, url: str | None, api_key: str | None, collection: str, timeout_seconds: float) -> None:
        if not url:
            raise ConfigurationError("QDRANT_URL is required when VECTOR_STORE=qdrant")
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.collection = collection
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {"api-key": self.api_key} if self.api_key else {}

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:  # pragma: no cover - external service
        import httpx

        points = [
            {"id": chunk.chunk_id, "vector": vector, "payload": chunk.as_dict()}
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        response = httpx.put(
            f"{self.url}/collections/{self.collection}/points?wait=true",
            headers=self._headers(),
            json={"points": points},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

    def search(
        self, vector: list[float], limit: int, language: str | None = None, cross_language: bool = False
    ) -> list[SearchHit]:  # pragma: no cover - external service
        import httpx

        query: dict[str, object] = {"vector": vector, "limit": limit, "with_payload": True}
        if language and not cross_language:
            query["filter"] = {"must": [{"key": "language", "match": {"value": language}}]}
        try:
            response = httpx.post(
                f"{self.url}/collections/{self.collection}/points/search",
                headers=self._headers(),
                json=query,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ServiceError("Vector database request failed") from exc
        result = response.json()["result"]
        return [
            SearchHit(
                chunk=Chunk.from_dict(point["payload"]),
                score=float(point["score"]),
                dense_score=float(point["score"]),
            )
            for point in result
        ]

    def count(self) -> int:  # pragma: no cover - external service
        import httpx

        response = httpx.post(
            f"{self.url}/collections/{self.collection}/points/count",
            headers=self._headers(),
            json={"exact": False},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return int(response.json()["result"]["count"])

    def health(self) -> bool:  # pragma: no cover - external service
        try:
            return self.count() >= 0
        except Exception:
            return False
