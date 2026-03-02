"""Chiplet model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class Chiplet:
    """Basic chiplet unit."""

    chiplet_id: str
