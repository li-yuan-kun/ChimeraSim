"""Memory model stubs."""

from dataclasses import dataclass


@dataclass(slots=True)
class Memory:
    """Minimal memory descriptor."""

    capacity_mb: int = 0
