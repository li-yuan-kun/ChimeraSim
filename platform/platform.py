from __future__ import annotations

from dataclasses import dataclass

from platform.config import PlatformConfig


@dataclass
class Platform:
    config: PlatformConfig

    @property
    def acim_tiles(self) -> int:
        return self.config.acim.num_tiles

    @property
    def digital_tiles(self) -> int:
        return self.config.digital.num_tiles
