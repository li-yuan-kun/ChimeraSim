"""Stats collection utilities."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class StatsCollector:
    """Collect scalar metrics for simulation runs."""

    metrics: dict[str, float] = field(default_factory=dict)

    def record(self, key: str, value: float) -> None:
        """Record a metric value."""
        self.metrics[key] = value
