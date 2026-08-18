from __future__ import annotations

import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    """Single-instance sliding-window limiter; deliberately not distributed."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, identity: str) -> bool:
        now = time.monotonic()
        events = self._events[identity]
        cutoff = now - self.window_seconds
        while events and events[0] < cutoff:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True
