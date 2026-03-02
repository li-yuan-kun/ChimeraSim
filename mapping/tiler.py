from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Protocol

from workload.graph import OpNode


@dataclass
class TileWorkItem:
    work_id: str
    op_id: str
    target: str
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    shots: int = 0
    meta: dict = field(default_factory=dict)


class Tiler(Protocol):
    def tile(self, op: OpNode, target: str, platform: object) -> list[TileWorkItem]:
        ...


class BlockTiler:
    """Split op payload by target tile count and estimate ACIM shots."""

    def tile(self, op: OpNode, target: str, platform: object) -> list[TileWorkItem]:
        cfg = platform.config.acim if target == "ACIM" else platform.config.digital
        n = max(1, cfg.num_tiles)

        def split(total: int, parts: int) -> list[int]:
            base, rem = divmod(total, parts)
            return [base + (1 if i < rem else 0) for i in range(parts)]

        ops_chunks = split(op.ops, n)
        in_chunks = split(op.in_bytes, n)
        w_chunks = split(op.w_bytes, n)
        out_chunks = split(op.out_bytes, n)

        items: list[TileWorkItem] = []
        for i in range(n):
            shots = 0
            if target == "ACIM":
                shots = ceil(ops_chunks[i] / max(1, cfg.ops_per_shot)) if ops_chunks[i] else 0
            items.append(
                TileWorkItem(
                    work_id=f"{op.op_id}:w{i}",
                    op_id=op.op_id,
                    target=target,
                    ops=ops_chunks[i],
                    in_bytes=in_chunks[i],
                    w_bytes=w_chunks[i],
                    out_bytes=out_chunks[i],
                    shots=shots,
                )
            )
        return items
