from __future__ import annotations

from app.services.types import SearchHit


def reciprocal_rank_fusion(lists: list[list[SearchHit]], limit: int, k: int = 60) -> list[SearchHit]:
    merged: dict[str, SearchHit] = {}
    scores: dict[str, float] = {}
    for ranked in lists:
        for rank, hit in enumerate(ranked, start=1):
            key = hit.chunk.chunk_id
            scores[key] = scores.get(key, 0.0) + 1 / (k + rank)
            existing = merged.get(key)
            if existing is None:
                merged[key] = hit
            else:
                merged[key] = SearchHit(
                    chunk=hit.chunk,
                    score=0,
                    dense_score=max(existing.dense_score, hit.dense_score),
                    lexical_score=max(existing.lexical_score, hit.lexical_score),
                )
    if not scores:
        return []
    maximum = max(scores.values())
    return [
        SearchHit(
            chunk=merged[key].chunk,
            score=value / maximum,
            dense_score=merged[key].dense_score,
            lexical_score=merged[key].lexical_score,
        )
        for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]
