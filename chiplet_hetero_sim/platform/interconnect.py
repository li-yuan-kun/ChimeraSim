"""Interconnect model stubs."""

from dataclasses import dataclass


@dataclass(slots=True)
class Interconnect:
    """Minimal interconnect description."""

    bandwidth_gbps: float = 0.0
