from __future__ import annotations

import asyncio
import random
import time

import httpx

from app.core.errors import ConfigurationError, ServiceError
from app.schemas.models import TranscriptResponse
from app.services.stt.base import SpeechToTextProvider


class SarvamSpeechToTextProvider(SpeechToTextProvider):
    """Sarvam Saaras v3 REST adapter for short (up to 30s) audio uploads."""

    def __init__(self, api_key: str | None, base_url: str, model: str, mode: str, timeout_seconds: float) -> None:
        if not api_key:
            raise ConfigurationError("SARVAM_API_KEY is required when DEMO_MODE=false")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mode = mode
        self.client = httpx.AsyncClient(timeout=timeout_seconds)

    async def transcribe(
        self, filename: str, content: bytes, content_type: str | None, language_hint: str | None = None
    ) -> TranscriptResponse:
        start = time.perf_counter()
        data: dict[str, str] = {"model": self.model, "mode": self.mode}
        if language_hint:
            data["language_code"] = language_hint
        files = {"file": (filename, content, content_type or "application/octet-stream")}
        for attempt in range(2):
            try:
                response = await self.client.post(
                    f"{self.base_url}/speech-to-text",
                    headers={"api-subscription-key": self.api_key},
                    data=data,
                    files=files,
                )
                response.raise_for_status()
                payload = response.json()
                transcript = str(payload.get("transcript", "")).strip()
                if not transcript:
                    raise ServiceError("Speech recognition returned an empty transcript", status_code=502)
                return TranscriptResponse(
                    transcript=transcript,
                    language=str(payload.get("language_code") or language_hint or "unknown"),
                    confidence=float(payload.get("confidence", 0.0) or 0.0),
                    provider="sarvam",
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500 and exc.response.status_code != 429:
                    raise ServiceError("Speech recognition failed. Please try again.", status_code=502) from exc
            except httpx.HTTPError:
                pass
            if attempt == 0:
                await asyncio.sleep(0.15 + random.random() * 0.1)
        raise ServiceError("Speech recognition failed. Please try again.")

    async def close(self) -> None:
        await self.client.aclose()
