from __future__ import annotations

from dataclasses import dataclass

from .config import DigitalTileConfig
from .memory import DRAM, MemoryResult


@dataclass(slots=True)
class DigitalResult:
    ops: int
    mem_bytes: int
    start_ns: float
    finish_ns: float
    mem_time_ns: float
    comp_time_ns: float
    queue_wait_ns: float
    energy_pj: float


class DigitalTile:
    def __init__(self, config: DigitalTileConfig, tile_id: str):
        self.config = config
        self.tile_id = tile_id
        self._served_tasks = 0
        self._busy_time_ns = 0.0
        self._queue_wait_ns = 0.0
        self._energy_pj = 0.0
        self._available_at_ns = 0.0

    def _compute_time_ns(self, ops: int) -> float:
        effective_ops = max(self.config.peak_ops_per_s * self.config.utilization, 1e-12)
        return ops / effective_ops * 1e9

    def submit(
        self,
        dram: DRAM,
        ops: int,
        mem_bytes: int,
        ready_time_ns: float = 0.0,
    ) -> DigitalResult:
        start_ns = max(self._available_at_ns, ready_time_ns)
        mem_result: MemoryResult = dram.submit(mem_bytes, ready_time_ns=start_ns)
        mem_time_ns = mem_result.finish_ns - start_ns
        comp_time_ns = self._compute_time_ns(ops)
        comp_energy_pj = ops * self.config.energy_pj_per_op

        if self.config.overlap_enabled:
            finish_ns = max(mem_result.finish_ns, start_ns + comp_time_ns)
        else:
            finish_ns = mem_result.finish_ns + comp_time_ns

        service_ns = finish_ns - start_ns
        queue_wait_ns = start_ns - ready_time_ns

        self._served_tasks += 1
        self._busy_time_ns += service_ns
        self._queue_wait_ns += queue_wait_ns
        self._energy_pj += mem_result.energy_pj + comp_energy_pj
        self._available_at_ns = finish_ns

        return DigitalResult(
            ops=ops,
            mem_bytes=mem_bytes,
            start_ns=start_ns,
            finish_ns=finish_ns,
            mem_time_ns=mem_time_ns,
            comp_time_ns=comp_time_ns,
            queue_wait_ns=queue_wait_ns,
            energy_pj=mem_result.energy_pj + comp_energy_pj,
        )

    def report(self) -> dict:
        makespan_ns = max(self._available_at_ns, 1e-12)
        return {
            "tile_id": self.tile_id,
            "overlap_enabled": self.config.overlap_enabled,
            "served_tasks": self._served_tasks,
            "busy_time_ns": self._busy_time_ns,
            "queue_wait_ns": self._queue_wait_ns,
            "energy_pj": self._energy_pj,
            "utilization": self._busy_time_ns / makespan_ns,
        }
