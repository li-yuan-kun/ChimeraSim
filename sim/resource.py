"""Resource server with FCFS queue and capacity constraint."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

from sim.engine import SimEngine
from sim.stats import ResourceStats

DoneCallback = Callable[[Any, int, float], None]


@dataclass
class _QueuedItem:
    task: Any
    on_done: DoneCallback
    submit_time: int


class ResourceServer:
    """A generic FCFS service node backed by the simulation event engine."""

    def __init__(
        self,
        name: str,
        capacity: int,
        engine: SimEngine,
        service_rate_per_ns: float = 1.0,
        energy_per_unit_pj: float = 1.0,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if service_rate_per_ns <= 0:
            raise ValueError("service_rate_per_ns must be positive")

        self.name = name
        self.capacity = capacity
        self.engine = engine
        self.service_rate_per_ns = service_rate_per_ns
        self.energy_per_unit_pj = energy_per_unit_pj

        self.queue: deque[_QueuedItem] = deque()
        self.inflight: int = 0
        self.stats = ResourceStats()

    def submit(self, task: Any, on_done: DoneCallback) -> None:
        """Submit a task and trigger execution under FCFS/capacity rules."""
        self.queue.append(_QueuedItem(task=task, on_done=on_done, submit_time=self.engine.now))
        self._drain()

    def estimate(self, task: Any) -> tuple[int, float]:
        """Linear placeholder cost model: duration(ns), energy(pJ)."""
        work = float(getattr(task, "work", 0) or 0)
        if work <= 0:
            work = float(getattr(task, "ops", 0) or 0)
        if work <= 0:
            work = float(getattr(task, "bytes", 0) or 0)
        if work <= 0:
            work = float(getattr(task, "shots", 0) or 0)
        if work <= 0:
            work = 1.0

        duration_ns = max(1, int(work / self.service_rate_per_ns))
        energy_pj = work * self.energy_per_unit_pj
        return duration_ns, energy_pj

    def report(self) -> dict[str, float | int | str]:
        """Return a compact accounting snapshot for this resource."""
        total_time = self.engine.now
        return {
            "name": self.name,
            "capacity": self.capacity,
            "queue_len": len(self.queue),
            "inflight": self.inflight,
            "served_tasks": self.stats.served_tasks,
            "busy_time": self.stats.busy_time,
            "queue_time": self.stats.queue_time,
            "utilization": self.stats.utilization(total_time=total_time, capacity=self.capacity),
        }

    def _drain(self) -> None:
        while self.inflight < self.capacity and self.queue:
            item = self.queue.popleft()
            self.stats.queue_time += self.engine.now - item.submit_time

            duration_ns, energy_pj = self.estimate(item.task)
            self.inflight += 1
            self.stats.busy_time += duration_ns

            finish_time = self.engine.now + duration_ns
            self.engine.schedule(
                finish_time,
                self._complete,
                item.task,
                item.on_done,
                finish_time,
                energy_pj,
            )

    def _complete(self, task: Any, on_done: DoneCallback, finish_time: int, energy_pj: float) -> None:
        self.inflight -= 1
        self.stats.served_tasks += 1
        on_done(task, finish_time, energy_pj)
        self._drain()
