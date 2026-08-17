from __future__ import annotations

import re

from app.services.retrieval.bm25 import tokenize
from app.services.types import GroundingResult

_SENTENCES = re.compile(r"(?<=[.!?।])\s+")
_STOPWORDS = {"a", "an", "the", "is", "are", "of", "to", "and", "in", "that", "this", "it", "for", "with"}


class GroundingValidator:
    """Deterministic claim-overlap validation before a generated answer is returned."""

    def __init__(self, threshold: float = 0.45) -> None:
        self.threshold = threshold

    def validate(self, answer: str, context: str) -> GroundingResult:
        context_terms = set(tokenize(context))
        claims = [claim.strip() for claim in _SENTENCES.split(answer) if claim.strip()]
        unsupported: list[str] = []
        scores: list[float] = []
        for claim in claims:
            terms = {term for term in tokenize(claim) if term not in _STOPWORDS}
            if not terms:
                continue
            support = len(terms & context_terms) / len(terms)
            scores.append(support)
            if support < self.threshold:
                unsupported.append(claim)
        score = sum(scores) / len(scores) if scores else 0.0
        return GroundingResult(grounded=bool(scores) and not unsupported, support_score=score, unsupported_claims=unsupported)
