#!/usr/bin/env python3
"""
One-shot local status print (no server needed).

  python status.py
  python status.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.config import load_config
from core.dashboard import render
from core.stats import collect


def main() -> None:
    cfg = load_config()
    parser = argparse.ArgumentParser(description="SHAWPY local status")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    stats = collect()

    if args.json:
        payload = {
            "hostname": stats.hostname,
            "os": stats.os_name,
            "cpu": {
                "name": stats.cpu_name,
                "percent": stats.cpu_percent,
                "cores": stats.cpu_cores,
            },
            "ram": {
                "used_gb": round(stats.ram_used_gb, 2),
                "total_gb": round(stats.ram_total_gb, 2),
                "percent": round(stats.ram_percent, 1),
            },
            "disk": {
                "used_gb": round(stats.disk_used_gb, 1),
                "total_gb": round(stats.disk_total_gb, 1),
                "percent": round(stats.disk_percent, 1),
            },
            "gpu": {
                "available": stats.gpu.available,
                "name": stats.gpu.name,
                "temp_c": stats.gpu.temp_c,
                "util_pct": stats.gpu.util_pct,
                "vram_used_mib": stats.gpu.vram_used_mib,
                "vram_total_mib": stats.gpu.vram_total_mib,
            },
            "uptime": stats.uptime,
            "collected_at": stats.collected_at.isoformat(),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(
            render(
                stats,
                title=cfg["display"].get("title", "SHAWPY // STATUS"),
                width=cfg["display"].get("width", 42),
            )
        )


if __name__ == "__main__":
    main()
