from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.models import LatencyBreakdown


@dataclass
class PipelineState:
    request_id: str
    query: str
    transcript: str | None = None
    latency: LatencyBreakdown = field(default_factory=LatencyBreakdown)
