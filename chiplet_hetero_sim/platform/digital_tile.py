"""Digital tile definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class DigitalTile:
    """Minimal digital tile."""

    tile_id: str
