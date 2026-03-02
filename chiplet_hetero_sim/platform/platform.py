"""Platform model root."""

from dataclasses import dataclass, field

from .chiplet import Chiplet
from .config import PlatformConfig


@dataclass(slots=True)
class Platform:
    """Top-level platform containing chiplets."""

    config: PlatformConfig = field(default_factory=PlatformConfig)
    chiplets: list[Chiplet] = field(default_factory=list)
