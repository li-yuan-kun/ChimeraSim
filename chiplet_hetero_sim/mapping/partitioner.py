"""Partitioning interface."""

from chiplet_hetero_sim.workload.graph import WorkloadGraph


def partition_workload(graph: WorkloadGraph) -> list[WorkloadGraph]:
    """Split workload graph into partitions (stub)."""
    return [graph]
