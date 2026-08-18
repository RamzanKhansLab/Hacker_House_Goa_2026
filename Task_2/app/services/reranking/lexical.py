from __future__ import annotations

from app.services.retrieval.bm25 import tokenize
from app.services.types import SearchHit


class LexicalReranker:
    """Low-latency fallback reranker; replaceable by a cross encoder."""

    def rerank(self, query: str, candidates: list[SearchHit], limit: int) -> list[SearchHit]:
        terms = set(tokenize(query))
        rescored: list[SearchHit] = []
        for hit in candidates:
            text_terms = set(tokenize(hit.chunk.text))
            overlap = len(terms & text_terms) / max(1, len(terms))
            score = min(1.0, 0.65 * hit.score + 0.35 * overlap)
            rescored.append(
                SearchHit(
                    chunk=hit.chunk,
                    score=score,
                    dense_score=hit.dense_score,
                    lexical_score=hit.lexical_score,
                )
            )
        return sorted(rescored, key=lambda hit: hit.score, reverse=True)[:limit]
