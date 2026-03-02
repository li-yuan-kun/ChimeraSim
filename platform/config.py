from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ACIMTileConfig:
    num_arrays: int = 16
    num_adc_groups: int = 4
    num_dac_groups: int = 4
    t_dac_ns: float = 5.0
    t_array_ns: float = 10.0
    t_adc_ns: float = 20.0
    t_accum_ns: float = 5.0
    energy_pj_per_shot: float = 100.0


@dataclass(slots=True)
class DigitalTileConfig:
    num_mac_arrays: int = 2
    peak_ops_per_s: float = 2.0e12
    utilization: float = 0.7
    overlap_enabled: bool = True
    energy_pj_per_op: float = 1e-3


@dataclass(slots=True)
class NoPConfig:
    bandwidth_GBs: float = 256.0
    base_latency_ns: float = 50.0
    energy_pj_per_byte: float = 0.5


@dataclass(slots=True)
class DRAMConfig:
    bandwidth_GBs: float = 128.0
    base_latency_ns: float = 80.0
    energy_pj_per_byte: float = 2.0


@dataclass(slots=True)
class PlatformConfig:
    acim_num_tiles: int = 8
    dig_num_tiles: int = 4
    acim_tile: ACIMTileConfig = field(default_factory=ACIMTileConfig)
    dig_tile: DigitalTileConfig = field(default_factory=DigitalTileConfig)
    nop: NoPConfig = field(default_factory=NoPConfig)
    dram: DRAMConfig = field(default_factory=DRAMConfig)
