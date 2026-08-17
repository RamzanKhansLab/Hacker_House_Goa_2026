from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.models import TranscriptResponse


class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(
        self, filename: str, content: bytes, content_type: str | None, language_hint: str | None = None
    ) -> TranscriptResponse: ...

    async def close(self) -> None:
        return None
