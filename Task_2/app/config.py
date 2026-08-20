from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration is supplied by the environment or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "development"
    demo_mode: bool = True
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    allowed_origins: str = "http://localhost:5173"

    index_path: Path = Path("data/index/index.json")
    embedding_backend: str = "hash"
    embedding_model: str = "intfloat/multilingual-e5-small"
    vector_store: str = "local"
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection: str = "msmarco_xi"
    retrieve_top_k: int = Field(default=50, ge=1, le=100)
    rerank_top_k: int = Field(default=8, ge=1, le=32)
    grounding_threshold: float = Field(default=0.45, ge=0, le=1)
    max_query_chars: int = Field(default=512, ge=32, le=1000)
    max_context_tokens: int = Field(default=900, ge=100, le=4000)
    reranker_enabled: bool = True
    min_retrieval_score: float = Field(default=0.08, ge=0, le=1)

    sarvam_api_key: str | None = None
    sarvam_base_url: str = "https://api.sarvam.ai"
    sarvam_stt_model: str = "saaras:v3"
    # Preserve what the speaker said in its original language.  ``codemix``
    # remains available as an explicit deployment choice.
    sarvam_stt_mode: str = "transcribe"
    stt_timeout_seconds: float = Field(default=20, ge=1, le=60)
    max_audio_size_mb: int = Field(default=8, ge=1, le=30)

    llm_provider: str = "mock"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_timeout_seconds: float = Field(default=12, ge=1, le=60)
    vector_db_timeout_seconds: float = Field(default=2, ge=0.1, le=20)
    max_concurrent_requests: int = Field(default=4, ge=1, le=32)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=300)
    query_cache_size: int = Field(default=128, ge=0, le=1024)

    @field_validator("allowed_origins")
    @classmethod
    def origins_are_nonempty(cls, value: str) -> str:
        return value.strip()

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_audio_bytes(self) -> int:
        return self.max_audio_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
