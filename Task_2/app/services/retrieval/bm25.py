from __future__ import annotations

import math
import re
from collections import Counter

from app.services.types import Chunk, SearchHit

_WORD = re.compile(r"[\w\u0900-\u0d7f]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


class BM25Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.2, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.tokens = [tokenize(chunk.text) for chunk in chunks]
        self.avgdl = sum(len(row) for row in self.tokens) / max(1, len(self.tokens))
        self.document_frequency: Counter[str] = Counter()
        for row in self.tokens:
            self.document_frequency.update(set(row))

    def search(
        self, query: str, limit: int, language: str | None = None, cross_language: bool = False
    ) -> list[SearchHit]:
        query_terms = tokenize(query)
        selected = [index for index, chunk in enumerate(self.chunks) if not language or cross_language or chunk.language == language]
        if not selected:
            selected = list(range(len(self.chunks)))
        total = len(self.chunks)
        result: list[SearchHit] = []
        for index in selected:
            row = self.tokens[index]
            frequencies = Counter(row)
            score = 0.0
            for term in query_terms:
                frequency = self.document_frequency.get(term, 0)
                if not frequency:
                    continue
                idf = math.log(1 + (total - frequency + 0.5) / (frequency + 0.5))
                tf = frequencies[term]
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * len(row) / self.avgdl))
            if score > 0:
                result.append(SearchHit(chunk=self.chunks[index], score=score, lexical_score=score))
        return sorted(result, key=lambda hit: hit.score, reverse=True)[:limit]
