from __future__ import annotations

from typing import cast

from fastapi import APIRouter, HTTPException, Request, status

from app.core.dependencies import ApplicationServices
from app.schemas import AnswerResponse, QueryRequest

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=AnswerResponse)
async def query(payload: QueryRequest, request: Request) -> AnswerResponse:
    services = cast(ApplicationServices, request.app.state.services)
    if not services.rate_limiter.allowed(request.client.host if request.client else "unknown"):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Try again shortly.")
    return await services.orchestrator.answer(payload.query, payload.language, payload.cross_language)
