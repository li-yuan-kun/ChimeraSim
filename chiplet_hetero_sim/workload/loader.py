"""Workload loading helpers."""

from pathlib import Path

from .graph import WorkloadGraph


def load_workload(path: str | Path) -> WorkloadGraph:
    """Load workload from file path (stub)."""
    _ = Path(path)
    return WorkloadGraph()
