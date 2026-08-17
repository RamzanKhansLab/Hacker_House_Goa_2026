from __future__ import annotations

import re

from app.services.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic context-only generator used by demo mode and tests."""

    async def generate(self, query: str, context: str, language: str) -> str:
        del query, language
        content = re.sub(r"\[Source: [^\]]+\]\s*", "", context).strip()
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?।])\s+", content) if sentence.strip()]
        return " ".join(sentences[:2]) if sentences else "I don't have enough information in the retrieved context."
