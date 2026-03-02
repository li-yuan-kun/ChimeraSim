"""Trace record helpers."""

from dataclasses import dataclass


@dataclass(slots=True)
class TraceEvent:
    """A single trace event."""

    name: str
    ts: int
