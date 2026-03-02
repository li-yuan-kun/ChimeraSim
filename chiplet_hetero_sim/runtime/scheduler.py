"""Runtime scheduling stubs."""

from collections.abc import Sequence

from chiplet_hetero_sim.sim.task import SimTask


class Scheduler:
    """Minimal scheduler interface."""

    def schedule(self, tasks: Sequence[SimTask]) -> list[SimTask]:
        """Return an execution order for tasks."""
        return list(tasks)
