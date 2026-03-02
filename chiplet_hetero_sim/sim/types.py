"""Core type definitions for simulation."""

from dataclasses import dataclass
from enum import Enum


class TaskState(str, Enum):
    """Execution state of a task."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"


@dataclass(slots=True)
class Timestamp:
    """Simple timestamp wrapper in cycles."""

    cycle: int = 0
