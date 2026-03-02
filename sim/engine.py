"""Discrete event simulation engine."""

from __future__ import annotations

import heapq
import itertools
from typing import Any, Callable


class SimEngine:
    """A tiny event engine with timestamp-ordered callback execution."""

    def __init__(self) -> None:
        self.now: int = 0
        self._events: list[tuple[int, int, Callable[..., Any], tuple[Any, ...]]] = []
        self._seq = itertools.count()

    def schedule(self, ts: int, callback: Callable[..., Any], *args: Any) -> None:
        """Schedule ``callback(*args)`` to run at simulation timestamp ``ts``."""
        if ts < self.now:
            raise ValueError(f"cannot schedule event in the past: ts={ts}, now={self.now}")
        heapq.heappush(self._events, (ts, next(self._seq), callback, args))

    def run(self, until: int | None = None) -> None:
        """Run queued events in timestamp order.

        When ``until`` is provided, events with timestamp ``> until`` are not executed.
        """
        if until is not None and until < self.now:
            raise ValueError(f"'until' cannot be earlier than now: until={until}, now={self.now}")

        while self._events:
            ts, seq, callback, args = heapq.heappop(self._events)
            if until is not None and ts > until:
                heapq.heappush(self._events, (ts, seq, callback, args))
                self.now = until
                return

            self.now = ts
            callback(*args)

        if until is not None:
            self.now = until
