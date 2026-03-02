"""Workload profile definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class WorkloadProfile:
    """Simple workload profile."""

    name: str
    batch_size: int = 1
