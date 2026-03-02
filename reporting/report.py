from __future__ import annotations

from collections import Counter


def build_report(runtime_result: dict) -> dict:
    tasks = runtime_result["tasks"]
    counts = Counter(t["kind"] for t in tasks)
    return {
        "total_latency_ns": runtime_result["total_latency_ns"],
        "num_ops": len(runtime_result["op_finish_ns"]),
        "task_breakdown": dict(counts),
        "op_start_ns": runtime_result["op_start_ns"],
        "op_finish_ns": runtime_result["op_finish_ns"],
    }
