"""Analog CIM tile definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class ACIMTile:
    """Minimal analog CIM tile."""

    tile_id: str
