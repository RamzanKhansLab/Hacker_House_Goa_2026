import asyncio

from app.services.stt import MockSpeechToTextProvider
from app.services.stt.sarvam import sarvam_language_code


def test_mock_stt_has_structured_result() -> None:
    result = asyncio.run(MockSpeechToTextProvider().transcribe("audio.webm", b"audio", "audio/webm", "hi-IN"))
    assert result.provider == "mock"
    assert result.language == "hi-IN"
    assert result.transcript


def test_sarvam_language_hints_are_explicit_or_auto_detected() -> None:
    assert sarvam_language_code(None) == "unknown"
    assert sarvam_language_code("") == "unknown"
    assert sarvam_language_code("en") == "en-IN"
    assert sarvam_language_code("hi") == "hi-IN"
    assert sarvam_language_code("mr-IN") == "mr-IN"
