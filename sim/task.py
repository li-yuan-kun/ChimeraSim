from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: str
    kind: str
    bytes: int = 0
    ops: int = 0
    shots: int = 0
    src: str | None = None
    dst: str | None = None
    start_ns: float = 0.0
    end_ns: float = 0.0
    meta: dict = field(default_factory=dict)
