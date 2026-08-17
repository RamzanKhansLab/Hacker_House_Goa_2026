from __future__ import annotations

from collections.abc import Iterable


def quality_metrics(rankings: Iterable[tuple[str, list[str]]]) -> dict[str, float]:
    items = list(rankings)
    if not items:
        return {"mrr": 0.0, "hit_rate": 0.0, **{f"recall_at_{k}": 0.0 for k in (1, 3, 5, 10)}}
    mrr = 0.0
    hits: dict[int, int] = {k: 0 for k in (1, 3, 5, 10)}
    for expected, ranked in items:
        rank = next((index + 1 for index, candidate in enumerate(ranked) if candidate == expected), None)
        if rank:
            mrr += 1 / rank
            for k in hits:
                if rank <= k:
                    hits[k] += 1
    total = len(items)
    return {
        "mrr": round(mrr / total, 4),
        "hit_rate": round(hits[10] / total, 4),
        **{f"recall_at_{k}": round(value / total, 4) for k, value in hits.items()},
    }
