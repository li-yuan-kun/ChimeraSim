"""Basic statistics container for resource-level accounting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResourceStats:
    """Accumulates busy/queue accounting and served task counters."""

    busy_time: int = 0
    queue_time: int = 0
    served_tasks: int = 0

    def utilization(self, total_time: int, capacity: int = 1) -> float:
        """Return resource utilization in [0, 1] under the given window."""
        if total_time <= 0 or capacity <= 0:
            return 0.0
        return min(1.0, self.busy_time / float(total_time * capacity))
