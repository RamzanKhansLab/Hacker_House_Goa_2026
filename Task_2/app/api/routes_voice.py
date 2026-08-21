from __future__ import annotations

import logging
from pathlib import Path
from typing import cast

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.core.dependencies import ApplicationServices
from app.core.errors import InvalidAudioError
from app.schemas import AnswerResponse

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/m4a", "audio/ogg",
    "audio/opus", "audio/webm", "audio/flac", "audio/aac", "audio/x-aac",
}
_EXTENSION_TYPES = {
    ".wav": {"audio/wav", "audio/x-wav"},
    ".mp3": {"audio/mpeg", "audio/mp3"},
    ".m4a": {"audio/m4a", "audio/x-m4a", "audio/mp4"},
    ".mp4": {"audio/mp4"},
    ".ogg": {"audio/ogg", "audio/opus"},
    ".opus": {"audio/opus", "audio/ogg"},
    ".webm": {"audio/webm"},
    ".flac": {"audio/flac"},
    ".aac": {"audio/aac", "audio/x-aac"},
}


def _normalized_media_type(content_type: str | None) -> str | None:
    """Drop MIME parameters such as ``;codecs=opus`` before allow-listing."""
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower() or None


def _validate_audio_type(filename: str | None, content_type: str | None) -> str:
    media_type = _normalized_media_type(content_type)
    suffix = Path(filename or "").suffix.lower()
    allowed_for_extension = _EXTENSION_TYPES.get(suffix)
    if media_type and media_type not in _AUDIO_TYPES:
        raise InvalidAudioError("Unsupported audio type. Use WAV, MP3, M4A, OGG, WebM, FLAC, or AAC.")
    if not allowed_for_extension:
        raise InvalidAudioError("Unsupported audio filename. Use a supported audio file extension.")
    if media_type and media_type not in allowed_for_extension:
        raise InvalidAudioError("Audio filename and MIME type do not match.")
    return media_type or next(iter(allowed_for_extension))


@router.post("", response_model=AnswerResponse)
async def voice_query(
    request: Request,
    audio: UploadFile = File(..., description="Audio under 30 seconds for Sarvam REST STT"),
    language_hint: str | None = Form(default=None),
    cross_language: bool = Form(default=False),
) -> AnswerResponse:
    services = cast(ApplicationServices, request.app.state.services)
    if not services.rate_limiter.allowed(request.client.host if request.client else "unknown"):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Try again shortly.")
    media_type = _validate_audio_type(audio.filename, audio.content_type)
    content = await audio.read()
    if not content:
        raise InvalidAudioError("Audio file is empty.")
    if len(content) > services.settings.max_audio_bytes:
        raise InvalidAudioError(f"Audio exceeds the {services.settings.max_audio_size_mb} MB limit.")
    logger.info(
        "voice_upload_received",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "upload_filename": audio.filename,
            "mime": media_type,
            "audio_bytes": len(content),
            "stt_provider": "mock" if services.settings.demo_mode else "sarvam",
            "stt_model": services.settings.sarvam_stt_model,
            "stt_mode": services.settings.sarvam_stt_mode,
        },
    )
    transcript = await services.stt.transcribe(audio.filename or "recording.webm", content, media_type, language_hint)
    detected_language = transcript.language.split("-", 1)[0].lower()
    if detected_language in {"", "unknown"}:
        detected_language = services.orchestrator.analyzer.detect_language(transcript.transcript)
    answer = await services.orchestrator.answer(
        transcript.transcript, detected_language, cross_language, transcript.transcript
    )
    latency = answer.latency.model_copy(update={"stt_ms": transcript.latency_ms})
    latency.end_to_end_ms = latency.rag_total_ms + latency.stt_ms
    return answer.model_copy(update={"latency": latency})
