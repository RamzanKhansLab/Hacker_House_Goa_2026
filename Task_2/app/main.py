from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_health import router as health_router
from app.api.routes_metrics import router as metrics_router
from app.api.routes_query import router as query_router
from app.api.routes_voice import router as voice_router
from app.config import get_settings
from app.core.dependencies import create_services
from app.core.errors import ServiceError
from app.core.middleware import RequestContextMiddleware
from app.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.services = create_services(settings)
    logging.getLogger(__name__).info("application_ready", extra={"status": "ready"})
    yield
    await app.state.services.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Goa Voice RAG API",
        version="0.1.0",
        description="Multilingual hybrid RAG with Sarvam STT and deterministic guardrails.",
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )
    app.include_router(health_router)
    app.include_router(query_router, prefix=settings.api_prefix)
    app.include_router(voice_router, prefix=settings.api_prefix)
    app.include_router(metrics_router, prefix=settings.api_prefix)

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"request_id": getattr(request.state, "request_id", None), "error": exc.code, "detail": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"request_id": getattr(request.state, "request_id", None), "error": "validation_error", "detail": exc.errors()},
        )
    return app


app = create_app()
