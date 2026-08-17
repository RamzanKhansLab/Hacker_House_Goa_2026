from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/metrics", tags=["observability"])


@router.get("")
async def metrics(request: Request) -> dict[str, object]:
    services = request.app.state.services
    return {
        "index_document_chunks": services.store.count(),
        "query_cache_entries": len(services.orchestrator.cache),
        "demo_mode": services.settings.demo_mode,
        "note": "Development metrics only; do not expose internal query content in production.",
    }
