import asyncio

from app.services.stt import MockSpeechToTextProvider


def test_mock_stt_has_structured_result() -> None:
    result = asyncio.run(MockSpeechToTextProvider().transcribe("audio.webm", b"audio", "audio/webm", "hi-IN"))
    assert result.provider == "mock"
    assert result.language == "hi-IN"
    assert result.transcript
