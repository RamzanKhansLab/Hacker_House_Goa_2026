from __future__ import annotations

import time

from app.schemas.models import TranscriptResponse
from app.services.stt.base import SpeechToTextProvider


class MockSpeechToTextProvider(SpeechToTextProvider):
    async def transcribe(
        self, filename: str, content: bytes, content_type: str | None, language_hint: str | None = None
    ) -> TranscriptResponse:
        del filename, content, content_type
        start = time.perf_counter()
        # A deterministic fixture makes the browser demo runnable without keys.
        return TranscriptResponse(
            transcript="What is retrieval augmented generation?",
            language=language_hint or "en-IN",
            confidence=1.0,
            provider="mock",
            latency_ms=(time.perf_counter() - start) * 1000,
        )
