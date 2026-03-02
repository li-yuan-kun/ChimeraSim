from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TileWorkItem:
    work_id: str
    op_id: str
    target: str
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    shots: int = 0
    meta: dict[str, Any] = field(default_factory=dict)
