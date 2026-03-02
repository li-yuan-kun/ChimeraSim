from __future__ import annotations

from collections import deque

from mapping.tiler import TileWorkItem, Tiler
from sim.task import Task
from workload.graph import WorkloadGraph


class GraphRuntime:
    def __init__(self, graph: WorkloadGraph, platform: object, mapping: dict[str, str], tiler: Tiler):
        self.graph = graph
        self.platform = platform
        self.mapping = mapping
        self.tiler = tiler

        self._pending_preds = {op_id: len(op.preds) for op_id, op in graph.nodes.items()}
        self._ready = deque([op_id for op_id, n in self._pending_preds.items() if n == 0])
        self._done_ops: set[str] = set()
        self.op_finish: dict[str, float] = {}
        self.op_start: dict[str, float] = {}

        self.acim_tile_free = [0.0] * platform.config.acim.num_tiles
        self.digital_tile_free = [0.0] * platform.config.digital.num_tiles
        self.nop_free = 0.0
        self.tasks: list[Task] = []

    def run(self) -> dict:
        while self._ready:
            op_id = self._ready.popleft()
            self._execute_op(op_id)

        total = max(self.op_finish.values(), default=0.0)
        return {
            "total_latency_ns": total,
            "op_start_ns": self.op_start,
            "op_finish_ns": self.op_finish,
            "tasks": [task.__dict__ for task in self.tasks],
        }

    def _execute_op(self, op_id: str) -> None:
        op = self.graph.get_op(op_id)
        target = self.mapping[op_id]
        pred_done = max((self.op_finish[p] for p in op.preds), default=0.0)
        ready_time = pred_done

        if any(self.mapping[p] != target for p in op.preds):
            comm_start = max(self.nop_free, pred_done)
            comm_time = self.platform.config.nop.latency_ns + (
                op.in_bytes / max(1e-9, self.platform.config.nop.bandwidth_bytes_per_ns)
            )
            comm_end = comm_start + comm_time
            self.nop_free = comm_end
            ready_time = comm_end
            self.tasks.append(
                Task(
                    task_id=f"{op_id}:comm",
                    kind="COMM",
                    bytes=op.in_bytes,
                    src="CROSS_CHIPLET",
                    dst=target,
                    start_ns=comm_start,
                    end_ns=comm_end,
                )
            )

        work_items = self.tiler.tile(op, target, self.platform)
        self.op_start[op_id] = ready_time
        finishes: list[float] = []
        for item in work_items:
            finishes.append(self._schedule_work(item, ready_time))

        done = max(finishes, default=ready_time)
        self.op_finish[op_id] = done
        self._done_ops.add(op_id)

        for succ in op.succs:
            self._pending_preds[succ] -= 1
            if self._pending_preds[succ] == 0:
                self._ready.append(succ)

    def _schedule_work(self, item: TileWorkItem, ready_time: float) -> float:
        if item.target == "ACIM":
            idx = min(range(len(self.acim_tile_free)), key=self.acim_tile_free.__getitem__)
            start = max(ready_time, self.acim_tile_free[idx])
            cfg = self.platform.config.acim
            dur = max(
                item.ops / max(1e-9, cfg.ops_per_ns),
                item.shots / max(1e-9, cfg.shots_per_ns),
            )
            end = start + dur
            self.acim_tile_free[idx] = end
            kind = "ACIM_SHOT"
        else:
            idx = min(range(len(self.digital_tile_free)), key=self.digital_tile_free.__getitem__)
            start = max(ready_time, self.digital_tile_free[idx])
            cfg = self.platform.config.digital
            dur = item.ops / max(1e-9, cfg.ops_per_ns)
            end = start + dur
            self.digital_tile_free[idx] = end
            kind = "DIGITAL_COMP"

        self.tasks.append(
            Task(
                task_id=item.work_id,
                kind=kind,
                ops=item.ops,
                bytes=item.in_bytes + item.w_bytes + item.out_bytes,
                shots=item.shots,
                dst=f"{item.target}_tile_{idx}",
                start_ns=start,
                end_ns=end,
            )
        )
        return end
