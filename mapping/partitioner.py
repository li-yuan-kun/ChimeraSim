from __future__ import annotations

from typing import Protocol

from workload.graph import WorkloadGraph


class Partitioner(Protocol):
    def assign(self, graph: WorkloadGraph, platform: object) -> dict[str, str]:
        ...


class RuleBasedPartitioner:
    """Map GEMM/MATMUL/CONV to ACIM by default, others to DIGITAL."""

    ACIM_OPS = {"GEMM", "MATMUL", "CONV"}

    def assign(self, graph: WorkloadGraph, platform: object) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for op_id in graph.topological():
            op = graph.get_op(op_id)
            mapping[op_id] = "ACIM" if op.op_type.upper() in self.ACIM_OPS else "DIGITAL"
        return mapping
