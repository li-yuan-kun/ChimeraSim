from __future__ import annotations

import json
from pathlib import Path

from workload.graph import OpNode, WorkloadGraph


def _load_struct(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text())
    except ModuleNotFoundError as exc:
        raise RuntimeError("YAML input requires PyYAML; use JSON file instead") from exc


def load_workload(path: str) -> WorkloadGraph:
    data = _load_struct(Path(path))
    ops = [OpNode(**item) for item in data["ops"]]
    return WorkloadGraph(ops)
