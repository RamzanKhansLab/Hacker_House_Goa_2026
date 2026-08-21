from __future__ import annotations

import time
from uuid import NAMESPACE_URL, uuid5

from app.core.errors import ConfigurationError, ServiceError
from app.services.retrieval.base import VectorStore
from app.services.types import Chunk, SearchHit


class QdrantVectorStore(VectorStore):
    """REST adapter for Qdrant."""

    def __init__(
        self,
        url: str | None,
        api_key: str | None,
        collection: str,
        timeout_seconds: float,
    ) -> None:
        if not url:
            raise ConfigurationError(
                "QDRANT_URL is required when VECTOR_STORE=qdrant"
            )

        self.url = url.rstrip("/")
        self.api_key = api_key
        self.collection = collection
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            **({"api-key": self.api_key} if self.api_key else {}),
        }

    def upsert(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:  # pragma: no cover - external service
        import httpx

        if len(chunks) != len(vectors):
            raise ValueError(
                f"Chunks/vectors length mismatch: "
                f"{len(chunks)} chunks vs {len(vectors)} vectors"
            )

        points = [
            {
                # Qdrant accepts UUIDs as point IDs.
                # uuid5 makes the ID deterministic, so re-running ingestion
                # updates the same point instead of creating duplicates.
                "id": str(uuid5(NAMESPACE_URL, chunk.chunk_id)),
                "vector": vector,
                # Original chunk_id remains inside the payload.
                "payload": chunk.as_dict(),
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

        last_error: Exception | None = None

        for attempt in range(1, 6):
            try:
                response = httpx.put(
                    # wait=false prevents long server-side indexing waits
                    # from blocking every upload batch.
                    f"{self.url}/collections/"
                    f"{self.collection}/points?wait=false",
                    headers=self._headers(),
                    json={"points": points},
                    timeout=httpx.Timeout(
                        connect=30.0,
                        read=max(self.timeout_seconds, 120.0),
                        write=max(self.timeout_seconds, 120.0),
                        pool=30.0,
                    ),
                )

                if response.is_error:
                    print(
                        "Qdrant upsert failed "
                        f"({response.status_code}): "
                        f"{response.text}"
                    )

                response.raise_for_status()
                return

            except (
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.ConnectTimeout,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            ) as exc:
                last_error = exc

                print(
                    f"Qdrant temporary network error "
                    f"(attempt {attempt}/5): "
                    f"{type(exc).__name__}"
                )

                if attempt < 5:
                    delay = attempt * 2

                    print(
                        f"Retrying Qdrant batch "
                        f"in {delay} seconds..."
                    )

                    time.sleep(delay)

            except httpx.HTTPStatusError as exc:
                response_text = ""

                if exc.response is not None:
                    response_text = exc.response.text

                raise ServiceError(
                    "Qdrant rejected the upsert request. "
                    f"Status: {exc.response.status_code if exc.response else 'unknown'}. "
                    f"Response: {response_text}"
                ) from exc

            except httpx.HTTPError as exc:
                last_error = exc

                print(
                    f"Qdrant HTTP error "
                    f"(attempt {attempt}/5): "
                    f"{type(exc).__name__}: {exc}"
                )

                if attempt < 5:
                    delay = attempt * 2

                    print(
                        f"Retrying Qdrant batch "
                        f"in {delay} seconds..."
                    )

                    time.sleep(delay)

        raise ServiceError(
            "Qdrant upsert failed after 5 attempts. "
            f"Last error: {last_error}"
        )

    def search(
        self,
        vector: list[float],
        limit: int,
        language: str | None = None,
        cross_language: bool = False,
    ) -> list[SearchHit]:  # pragma: no cover - external service
        import httpx

        query: dict[str, object] = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }

        if language and not cross_language:
            query["filter"] = {
                "must": [
                    {
                        "key": "language",
                        "match": {
                            "value": language,
                        },
                    }
                ]
            }

        try:
            response = httpx.post(
                f"{self.url}/collections/"
                f"{self.collection}/points/search",
                headers=self._headers(),
                json=query,
                timeout=httpx.Timeout(
                    connect=30.0,
                    read=max(self.timeout_seconds, 60.0),
                    write=max(self.timeout_seconds, 60.0),
                    pool=30.0,
                ),
            )

            if response.is_error:
                print(
                    "Qdrant search failed "
                    f"({response.status_code}): "
                    f"{response.text}"
                )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise ServiceError(
                "Vector database search request failed"
            ) from exc

        data = response.json()
        result = data.get("result", [])

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

        try:
            response = httpx.post(
                f"{self.url}/collections/"
                f"{self.collection}/points/count",
                headers=self._headers(),
                json={
                    "exact": True,
                },
                timeout=httpx.Timeout(
                    connect=30.0,
                    read=max(self.timeout_seconds, 60.0),
                    write=max(self.timeout_seconds, 60.0),
                    pool=30.0,
                ),
            )

            if response.is_error:
                print(
                    "Qdrant count failed "
                    f"({response.status_code}): "
                    f"{response.text}"
                )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise ServiceError(
                "Qdrant count request failed"
            ) from exc

        return int(
            response.json()["result"]["count"]
        )

    def health(self) -> bool:  # pragma: no cover - external service
        try:
            return self.count() >= 0
        except Exception:
            return False