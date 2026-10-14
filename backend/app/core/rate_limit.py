"""Small in-memory sliding-window rate limiter exposed as a FastAPI dependency.

Per-process only. Behind several workers or instances, use a shared store
(e.g. Redis) instead. See docs/known-limitations.md.
"""
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import HTTPException, Request

from app.core.config import get_settings


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> int | None:
        """Record a hit. Return None if allowed, else seconds until retry."""
        now = self._clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return max(1, int(self.window - (now - hits[0])) + 1)
            hits.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_ALL_LIMITERS: list[RateLimiter] = []


def reset_all_limiters() -> None:
    for limiter in _ALL_LIMITERS:
        limiter.reset()


def _enabled() -> bool:
    return get_settings().rate_limit_enabled


def rate_limit(limit: int, window_seconds: int) -> Callable[[Request], None]:
    """Build a dependency allowing `limit` requests per `window_seconds` per client IP."""
    limiter = RateLimiter(limit, window_seconds)
    _ALL_LIMITERS.append(limiter)

    def dependency(request: Request) -> None:
        if not _enabled():
            return
        client = request.client.host if request.client else "unknown"
        retry_after = limiter.check(client)
        if retry_after is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency
