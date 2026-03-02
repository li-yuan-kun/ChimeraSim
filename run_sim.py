from __future__ import annotations

import argparse
import json

from mapping.partitioner import RuleBasedPartitioner
from mapping.tiler import BlockTiler
from platform.config import load_platform_config
from platform.platform import Platform
from reporting.report import build_report
from runtime.scheduler import GraphRuntime
from workload.loader import load_workload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ChimeraSim toy simulation")
    parser.add_argument("--config", required=True, help="Platform config YAML path")
    parser.add_argument("--workload", required=True, help="Workload YAML/JSON path")
    args = parser.parse_args()

    platform = Platform(load_platform_config(args.config))
    graph = load_workload(args.workload)

    mapping = RuleBasedPartitioner().assign(graph, platform)
    runtime = GraphRuntime(graph=graph, platform=platform, mapping=mapping, tiler=BlockTiler())
    result = runtime.run()
    report = build_report(result)

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
