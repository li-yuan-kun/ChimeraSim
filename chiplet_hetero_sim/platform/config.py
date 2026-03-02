"""Platform configuration types."""

from dataclasses import dataclass


@dataclass(slots=True)
class PlatformConfig:
    """Minimal platform config."""

    name: str = "default"
