"""In-memory sliding-window counters, used to slow down brute-force attempts.

The counts live in the API process: they reset on restart and are not shared between
processes. That is enough for a single API container; several replicas would need a
shared store (PostgreSQL or Redis) instead.
"""

import time
from collections import deque
from collections.abc import Callable
from threading import Lock

# Above this many tracked keys, forget the ones whose events all expired
_CLEANUP_THRESHOLD = 10_000


class SlidingWindowCounter:
    """Counts events per key (an IP, an email...) over the last `window_seconds`."""

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._events: dict[str, deque[float]] = {}
        # FastAPI runs sync routes in a thread pool: guard the shared dictionary
        self._lock = Lock()

    def is_exceeded(self, key: str) -> bool:
        """True when `key` already reached the limit within the window."""
        with self._lock:
            return len(self._recent_events(key)) >= self.limit

    def record(self, key: str) -> None:
        """Count one event for `key` now."""
        with self._lock:
            self._recent_events(key).append(self._clock())
            if len(self._events) > _CLEANUP_THRESHOLD:
                self._forget_expired_keys()

    def reset(self) -> None:
        with self._lock:
            self._events.clear()

    def _recent_events(self, key: str) -> deque[float]:
        events = self._events.setdefault(key, deque())
        oldest_allowed = self._clock() - self.window_seconds
        while events and events[0] <= oldest_allowed:
            events.popleft()
        return events

    def _forget_expired_keys(self) -> None:
        for key in list(self._events):
            if not self._recent_events(key):
                del self._events[key]
