from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready")
async def ready(request: Request) -> dict[str, object]:
    services = request.app.state.services
    available = services.store.health()
    settings = services.settings
    return {
        "status": "ready" if available else "degraded",
        "index_ready": available,
        "index_manifest": services.manifest,
        "demo_mode": settings.demo_mode,
        # Operational metadata only: never expose the configured API key.
        "stt": {
            "provider": "mock" if settings.demo_mode else "sarvam",
            "model": settings.sarvam_stt_model,
            "mode": settings.sarvam_stt_mode,
        },
    }
