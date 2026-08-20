#!/usr/bin/env python3
"""
SHAWPY Status Monitor
Polls the status server and displays a live dashboard.

Usage:
  python monitor.py
  python monitor.py --server 192.168.1.10 --port 8000
  python monitor.py --refresh 1
"""

from __future__ import annotations

import argparse
import os
import platform
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.config import load_config
from core.dashboard import render_offline


def clear_screen() -> None:
    os.system("cls" if platform.system() == "Windows" else "clear")


def fetch_status(host: str, port: int, timeout: float) -> str:
    box_end = "╝".encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(b"STATUS\n")
        chunks: list[bytes] = []
        sock.settimeout(timeout)
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
                joined = b"".join(chunks)
                if joined.count(b"\n") >= 8 and (
                    joined.rstrip().endswith(box_end)
                    or b'"collected_at"' in joined
                ):
                    sock.settimeout(0.12)
                    try:
                        while True:
                            more = sock.recv(4096)
                            if not more:
                                break
                            chunks.append(more)
                    except socket.timeout:
                        pass
                    break
        except socket.timeout:
            if not chunks:
                raise
        return b"".join(chunks).decode("utf-8", errors="replace")


def main() -> None:
    cfg = load_config()
    mon = cfg["monitor"]
    display = cfg["display"]

    parser = argparse.ArgumentParser(
        description="SHAWPY Status Monitor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--server", "-s", default=mon["server"], help="Server hostname or IP")
    parser.add_argument("--port", "-p", type=int, default=mon["port"], help="Server port")
    parser.add_argument(
        "--refresh", "-r",
        type=float,
        default=mon.get("refresh_seconds", 2),
        help="Refresh interval in seconds",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=mon.get("connect_timeout", 5),
        help="Connection timeout in seconds",
    )
    args = parser.parse_args()

    title = display.get("title", "SHAWPY // STATUS")
    width = display.get("width", 42)

    print(f"SHAWPY Monitor → {args.server}:{args.port}")
    print(f"Refresh every {args.refresh}s  |  Ctrl+C to quit\n")
    time.sleep(0.6)

    consecutive_fails = 0

    try:
        while True:
            try:
                data = fetch_status(args.server, args.port, args.timeout)
                clear_screen()
                print(data)
                print(f"  ↻  every {args.refresh}s   ·   {args.server}:{args.port}   ·   Ctrl+C quit")
                consecutive_fails = 0
            except (socket.timeout, ConnectionRefusedError, OSError) as exc:
                consecutive_fails += 1
                clear_screen()
                err = str(exc)
                print(render_offline(error=err, title=title, width=width))
                print(f"  Retrying… (fail #{consecutive_fails})   ·   Ctrl+C quit")

            time.sleep(args.refresh)

    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
