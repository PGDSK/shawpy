"""Load and validate SHAWPY configuration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Default config lives next to the project root
_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PATH = _ROOT / "config.json"

_DEFAULTS: dict[str, Any] = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "max_clients": 8,
    },
    "monitor": {
        "server": "127.0.0.1",
        "port": 8000,
        "refresh_seconds": 2,
        "connect_timeout": 5,
    },
    "display": {
        "title": "SHAWPY // STATUS",
        "width": 42,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """
    Load config from JSON file, falling back to sensible defaults.
    Environment variables override file values:
      SHAWPY_HOST, SHAWPY_PORT, SHAWPY_MONITOR_SERVER
    """
    cfg = dict(_DEFAULTS)
    cfg_path = Path(path) if path else _DEFAULT_PATH

    if cfg_path.is_file():
        try:
            with open(cfg_path, encoding="utf-8") as f:
                file_cfg = json.load(f)
            if isinstance(file_cfg, dict):
                cfg = _deep_merge(cfg, file_cfg)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[config] Warning: could not load {cfg_path}: {exc}")

    # Environment overrides
    if host := os.environ.get("SHAWPY_HOST"):
        cfg["server"]["host"] = host
    if port := os.environ.get("SHAWPY_PORT"):
        try:
            cfg["server"]["port"] = int(port)
            cfg["monitor"]["port"] = int(port)
        except ValueError:
            pass
    if mon := os.environ.get("SHAWPY_MONITOR_SERVER"):
        cfg["monitor"]["server"] = mon

    return cfg
