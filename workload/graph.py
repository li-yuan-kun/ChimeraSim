from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque


@dataclass
class OpNode:
    op_id: str
    op_type: str
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    dtype: str = "fp16"
    preds: list[str] = field(default_factory=list)
    succs: list[str] = field(default_factory=list)


class WorkloadGraph:
    def __init__(self, ops: list[OpNode]) -> None:
        self.nodes: dict[str, OpNode] = {op.op_id: op for op in ops}
        for op in self.nodes.values():
            op.succs = []
        for op in self.nodes.values():
            for pred in op.preds:
                self.nodes[pred].succs.append(op.op_id)

    def topological(self) -> list[str]:
        indeg = {op_id: len(op.preds) for op_id, op in self.nodes.items()}
        q = deque([op_id for op_id, v in indeg.items() if v == 0])
        order: list[str] = []
        while q:
            cur = q.popleft()
            order.append(cur)
            for nxt in self.nodes[cur].succs:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    q.append(nxt)
        if len(order) != len(self.nodes):
            raise ValueError("Graph contains a cycle")
        return order

    def get_op(self, op_id: str) -> OpNode:
        return self.nodes[op_id]
