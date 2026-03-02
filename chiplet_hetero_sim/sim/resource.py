"""Simulation resources."""

from dataclasses import dataclass


@dataclass(slots=True)
class Resource:
    """A generic resource with capacity."""

    name: str
    capacity: int

    def available(self) -> int:
        """Return currently available capacity."""
        return self.capacity
