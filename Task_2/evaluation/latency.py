from __future__ import annotations

import math
from collections.abc import Iterable


def percentile(values: Iterable[float], percentile_value: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = (len(ordered) - 1) * percentile_value / 100
    lower, upper = math.floor(rank), math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


def latency_summary(rows: list[dict[str, float]], key: str) -> dict[str, float]:
    values = [row[key] for row in rows if key in row]
    return {f"p{level}": round(percentile(values, level), 3) for level in (50, 70, 90, 95, 99, 100)}
