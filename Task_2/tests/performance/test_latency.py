import asyncio

from app.config import Settings
from app.core.dependencies import create_services


def test_latency_schema_has_stage_breakdown() -> None:
    services = create_services(Settings(demo_mode=True, query_cache_size=0))
    try:
        answer = asyncio.run(services.orchestrator.answer("How does hybrid retrieval work?"))
        assert answer.latency.rag_total_ms >= 0
        assert answer.latency.embedding_ms >= 0
        assert answer.latency.dense_retrieval_ms >= 0
        assert answer.latency.lexical_retrieval_ms >= 0
    finally:
        asyncio.run(services.close())
