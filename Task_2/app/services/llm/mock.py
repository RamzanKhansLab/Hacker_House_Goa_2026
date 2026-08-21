from __future__ import annotations

import re

from app.services.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic context-only generator used by demo mode and tests."""

    async def generate(self, query: str, context: str, language: str) -> str:
        del query, language
        content = re.sub(r"\[Source: [^\]]+\]\s*", "", context).strip()
        # ``\u0964`` is the Hindi/Devanagari sentence delimiter.  Support it
        # explicitly so mock answers do not render an entire long passage.
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?\u0964])\s+", content) if sentence.strip()]
        if not sentences:
            return "I don't have enough information in the retrieved context."
        answer = " ".join(sentences[:2])
        # Some passages have no punctuation; retain a short, extractive answer.
        return " ".join(answer.split()[:100])
