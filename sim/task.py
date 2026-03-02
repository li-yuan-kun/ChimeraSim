from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

TaskKind = Literal["COMM", "MEM", "ACIM_SHOT", "DIGITAL_COMP"]


@dataclass(slots=True)
class Task:
    task_id: str
    kind: TaskKind
    bytes: int = 0
    ops: int = 0
    shots: int = 0
    src: str | None = None
    dst: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
