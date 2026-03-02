from __future__ import annotations

from dataclasses import dataclass

from .config import DRAMConfig


@dataclass(slots=True)
class MemoryResult:
    bytes: int
    start_ns: float
    finish_ns: float
    service_ns: float
    queue_wait_ns: float
    energy_pj: float


class DRAM:
    """DRAM FCFS server: bandwidth + base latency + energy per byte."""

    def __init__(self, config: DRAMConfig):
        self.config = config
        self._available_at_ns = 0.0
        self._served_tasks = 0
        self._busy_time_ns = 0.0
        self._queue_wait_ns = 0.0
        self._energy_pj = 0.0

    def _service_time_ns(self, num_bytes: int) -> float:
        transfer_ns = num_bytes / max(self.config.bandwidth_GBs, 1e-12)
        return self.config.base_latency_ns + transfer_ns

    def submit(self, num_bytes: int, ready_time_ns: float = 0.0) -> MemoryResult:
        service_ns = self._service_time_ns(num_bytes)
        start_ns = max(ready_time_ns, self._available_at_ns)
        finish_ns = start_ns + service_ns
        wait_ns = start_ns - ready_time_ns
        energy_pj = num_bytes * self.config.energy_pj_per_byte

        self._available_at_ns = finish_ns
        self._served_tasks += 1
        self._busy_time_ns += service_ns
        self._queue_wait_ns += wait_ns
        self._energy_pj += energy_pj

        return MemoryResult(
            bytes=num_bytes,
            start_ns=start_ns,
            finish_ns=finish_ns,
            service_ns=service_ns,
            queue_wait_ns=wait_ns,
            energy_pj=energy_pj,
        )

    def report(self) -> dict:
        makespan_ns = max(self._available_at_ns, 1e-12)
        return {
            "served_tasks": self._served_tasks,
            "busy_time_ns": self._busy_time_ns,
            "queue_wait_ns": self._queue_wait_ns,
            "energy_pj": self._energy_pj,
            "utilization": self._busy_time_ns / makespan_ns,
        }
