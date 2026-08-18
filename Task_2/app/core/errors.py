from __future__ import annotations


class ServiceError(Exception):
    def __init__(self, message: str, *, code: str = "service_error", status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class InvalidAudioError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="invalid_audio", status_code=400)


class ConfigurationError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="configuration_error", status_code=503)
