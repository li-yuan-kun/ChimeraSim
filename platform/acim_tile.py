from __future__ import annotations

import heapq
from dataclasses import dataclass

from .config import ACIMTileConfig


@dataclass(slots=True)
class ACIMResult:
    shots: int
    start_ns: float
    finish_ns: float
    service_ns: float
    queue_wait_ns: float
    energy_pj: float


class _ShotTokenServer:
    def __init__(self, capacity: int, shot_latency_ns: float):
        self.capacity = max(1, capacity)
        self.shot_latency_ns = shot_latency_ns
        self._token_free_ns = [0.0 for _ in range(self.capacity)]
        heapq.heapify(self._token_free_ns)

    def submit_shots(self, shots: int, ready_time_ns: float) -> tuple[float, float, float]:
        if shots <= 0:
            return ready_time_ns, ready_time_ns, 0.0

        first_start = None
        last_finish = ready_time_ns
        for _ in range(shots):
            token_free_ns = heapq.heappop(self._token_free_ns)
            start_ns = max(ready_time_ns, token_free_ns)
            finish_ns = start_ns + self.shot_latency_ns
            heapq.heappush(self._token_free_ns, finish_ns)
            if first_start is None:
                first_start = start_ns
            last_finish = max(last_finish, finish_ns)
        return first_start or ready_time_ns, last_finish, last_finish - (first_start or ready_time_ns)


class ACIMTile:
    def __init__(self, config: ACIMTileConfig, tile_id: str):
        self.config = config
        self.tile_id = tile_id
        self.parallel_shots = min(
            config.num_arrays,
            config.num_adc_groups,
            config.num_dac_groups,
        )
        self.t_shot_ns = config.t_dac_ns + config.t_array_ns + config.t_adc_ns + config.t_accum_ns
        self.shot_token_srv = _ShotTokenServer(self.parallel_shots, self.t_shot_ns)

        self._served_tasks = 0
        self._busy_time_ns = 0.0
        self._queue_wait_ns = 0.0
        self._energy_pj = 0.0
        self._available_at_ns = 0.0

    def submit_acim_shot(self, shots: int, ready_time_ns: float = 0.0) -> ACIMResult:
        start_ns, finish_ns, service_ns = self.shot_token_srv.submit_shots(
            shots=shots,
            ready_time_ns=ready_time_ns,
        )
        queue_wait_ns = max(0.0, start_ns - ready_time_ns)
        energy_pj = shots * self.config.energy_pj_per_shot

        self._served_tasks += 1
        self._busy_time_ns += service_ns
        self._queue_wait_ns += queue_wait_ns
        self._energy_pj += energy_pj
        self._available_at_ns = max(self._available_at_ns, finish_ns)

        return ACIMResult(
            shots=shots,
            start_ns=start_ns,
            finish_ns=finish_ns,
            service_ns=service_ns,
            queue_wait_ns=queue_wait_ns,
            energy_pj=energy_pj,
        )

    def report(self) -> dict:
        makespan_ns = max(self._available_at_ns, 1e-12)
        return {
            "tile_id": self.tile_id,
            "parallel_shots": self.parallel_shots,
            "served_tasks": self._served_tasks,
            "busy_time_ns": self._busy_time_ns,
            "queue_wait_ns": self._queue_wait_ns,
            "energy_pj": self._energy_pj,
            "utilization": self._busy_time_ns / makespan_ns,
        }
