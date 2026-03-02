from __future__ import annotations

from dataclasses import dataclass

from .acim_tile import ACIMTile
from .config import PlatformConfig
from .digital_tile import DigitalTile
from .interconnect import NoPInterconnect
from .memory import DRAM


@dataclass(slots=True)
class Chiplet:
    name: str
    tiles: list

    def report(self) -> dict:
        tile_reports = [tile.report() for tile in self.tiles]
        return {
            "name": self.name,
            "num_tiles": len(self.tiles),
            "tiles": tile_reports,
        }


class Platform:
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.nop = NoPInterconnect(config.nop)
        self.dram = DRAM(config.dram)

        self.acim_chiplet = Chiplet(
            name="ACIM",
            tiles=[ACIMTile(config.acim_tile, tile_id=f"acim_{i}") for i in range(config.acim_num_tiles)],
        )
        self.digital_chiplet = Chiplet(
            name="DIGITAL",
            tiles=[DigitalTile(config.dig_tile, tile_id=f"digital_{i}") for i in range(config.dig_num_tiles)],
        )

    def report(self) -> dict:
        acim_report = self.acim_chiplet.report()
        digital_report = self.digital_chiplet.report()

        total_energy_pj = (
            self.nop.report()["energy_pj"]
            + self.dram.report()["energy_pj"]
            + sum(tile["energy_pj"] for tile in acim_report["tiles"])
            + sum(tile["energy_pj"] for tile in digital_report["tiles"])
        )

        return {
            "acim_chiplet": acim_report,
            "digital_chiplet": digital_report,
            "nop": self.nop.report(),
            "dram": self.dram.report(),
            "total_energy_pj": total_energy_pj,
        }
