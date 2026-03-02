from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ChipletConfig:
    num_tiles: int
    ops_per_ns: float
    shots_per_ns: float = 1.0
    ops_per_shot: int = 1024


@dataclass
class NoPConfig:
    bandwidth_bytes_per_ns: float
    latency_ns: float


@dataclass
class PlatformConfig:
    acim: ChipletConfig
    digital: ChipletConfig
    nop: NoPConfig


def _load_struct(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text())
    except ModuleNotFoundError as exc:
        raise RuntimeError("YAML input requires PyYAML; use JSON file instead") from exc


def load_platform_config(path: str) -> PlatformConfig:
    raw = _load_struct(Path(path))
    return PlatformConfig(
        acim=ChipletConfig(**raw["acim"]),
        digital=ChipletConfig(**raw["digital"]),
        nop=NoPConfig(**raw["nop"]),
    )
