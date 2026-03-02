"""Workload graph model."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class WorkloadGraph:
    """Directed graph skeleton represented by adjacency list."""

    edges: dict[str, list[str]] = field(default_factory=dict)
