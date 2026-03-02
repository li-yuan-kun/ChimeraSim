"""Simulation engine entry points."""

from .stats import StatsCollector
from .task import SimTask


class SimulationEngine:
    """Minimal simulation engine skeleton."""

    def __init__(self) -> None:
        self.stats = StatsCollector()

    def submit(self, task: SimTask) -> None:
        """Submit a task into simulation engine."""
        _ = task

    def run(self) -> None:
        """Run one full simulation pass."""
        return None
