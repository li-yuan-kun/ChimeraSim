from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class OpNode:
    op_id: str
    op_type: str
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    dtype: str
    preds: list[str]
    succs: list[str]


class WorkloadGraph:
    def __init__(self, ops: list[OpNode]) -> None:
        self._ops = {op.op_id: op for op in ops}

    def topological(self) -> list[str]:
        indegree: dict[str, int] = {op_id: 0 for op_id in self._ops}
        for op in self._ops.values():
            for succ in op.succs:
                if succ not in self._ops:
                    raise KeyError(f"Unknown successor node: {succ}")
                indegree[succ] += 1

        queue = deque(op_id for op_id, degree in indegree.items() if degree == 0)
        order: list[str] = []

        while queue:
            op_id = queue.popleft()
            order.append(op_id)
            for succ in self._ops[op_id].succs:
                indegree[succ] -= 1
                if indegree[succ] == 0:
                    queue.append(succ)

        if len(order) != len(self._ops):
            raise ValueError("Workload graph contains cycles")

        return order

    def get_op(self, op_id: str) -> OpNode:
        return self._ops[op_id]
