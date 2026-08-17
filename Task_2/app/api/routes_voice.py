from __future__ import annotations

from typing import cast

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.core.dependencies import ApplicationServices
from app.core.errors import InvalidAudioError
from app.schemas import AnswerResponse

router = APIRouter(prefix="/voice", tags=["voice"])

_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/m4a", "audio/ogg",
    "audio/opus", "audio/webm", "audio/flac", "audio/aac", "audio/x-aac",
}


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
    if audio.content_type and audio.content_type not in _AUDIO_TYPES:
        raise InvalidAudioError("Unsupported audio type. Use WAV, MP3, M4A, OGG, WebM, FLAC, or AAC.")
    content = await audio.read()
    if not content:
        raise InvalidAudioError("Audio file is empty.")
    if len(content) > services.settings.max_audio_bytes:
        raise InvalidAudioError(f"Audio exceeds the {services.settings.max_audio_size_mb} MB limit.")
    transcript = await services.stt.transcribe(audio.filename or "recording.webm", content, audio.content_type, language_hint)
    answer = await services.orchestrator.answer(
        transcript.transcript, transcript.language.split("-")[0], cross_language, transcript.transcript
    )
    latency = answer.latency.model_copy(update={"stt_ms": transcript.latency_ms})
    latency.end_to_end_ms = latency.rag_total_ms + latency.stt_ms
    return answer.model_copy(update={"latency": latency})
