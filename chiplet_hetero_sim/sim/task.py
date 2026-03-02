"""Task domain objects."""

from dataclasses import dataclass, field
from typing import Any

from .types import TaskState


@dataclass(slots=True)
class SimTask:
    """Minimal task definition for simulator runtime."""

    task_id: str
    workload: Any = None
    state: TaskState = TaskState.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
