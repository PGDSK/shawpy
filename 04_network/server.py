#!/usr/bin/env python3
"""
SHAWPY Status Server
Cross-platform TCP server that answers STATUS requests with a live dashboard.

Usage:
  python server.py
  python server.py --host 0.0.0.0 --port 8000
  python server.py --json          # machine-readable responses
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import socket
import sys
import threading
from datetime import datetime
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.config import load_config
from core.dashboard import render
from core.stats import collect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("shawpy.server")


class StatusServer:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        max_clients: int = 8,
        json_mode: bool = False,
        title: str = "SHAWPY // STATUS",
        width: int = 42,
    ):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.json_mode = json_mode
        self.title = title
        self.width = width
        self._sock: socket.socket | None = None
        self._stop = threading.Event()
        self._clients = 0
        self._lock = threading.Lock()

    def _handle_client(self, client: socket.socket, address: tuple) -> None:
        peer = f"{address[0]}:{address[1]}"
        with self._lock:
            self._clients += 1
        log.info("Connected  %s  (active=%d)", peer, self._clients)

        try:
            client.settimeout(60.0)
            while not self._stop.is_set():
                try:
                    data = client.recv(1024)
                except socket.timeout:
                    continue
                if not data:
                    break

                message = data.decode(errors="replace").strip().upper()
                log.debug("  %s → %s", peer, message)

                if message in ("QUIT", "EXIT", "BYE"):
                    client.sendall(b"goodbye\n")
                    break

                if message == "STATUS":
                    stats = collect()
                    if self.json_mode:
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
                        response = json.dumps(payload, indent=2) + "\n"
                    else:
                        response = render(stats, title=self.title, width=self.width)
                elif message == "PING":
                    response = "PONG\n"
                else:
                    response = "Unknown command. Try: STATUS | PING | QUIT\n"

                client.sendall(response.encode("utf-8", errors="replace"))

        except (ConnectionResetError, BrokenPipeError, OSError) as exc:
            log.debug("Client %s error: %s", peer, exc)
        finally:
            try:
                client.close()
            except OSError:
                pass
            with self._lock:
                self._clients -= 1
            log.info("Disconnected  %s  (active=%d)", peer, self._clients)

    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._sock.bind((self.host, self.port))
        except OSError as exc:
            log.error("Cannot bind %s:%d → %s", self.host, self.port, exc)
            sys.exit(1)

        self._sock.listen(self.max_clients)
        self._sock.settimeout(1.0)  # so we can check _stop periodically

        log.info("Listening on %s:%d", self.host, self.port)
        log.info("Mode: %s", "JSON" if self.json_mode else "ASCII dashboard")
        log.info("Press Ctrl+C to stop")

        while not self._stop.is_set():
            try:
                client, address = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                if self._stop.is_set():
                    break
                raise

            t = threading.Thread(
                target=self._handle_client,
                args=(client, address),
                daemon=True,
                name=f"client-{address[0]}",
            )
            t.start()

    def stop(self) -> None:
        log.info("Shutting down...")
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass


def main() -> None:
    cfg = load_config()

    parser = argparse.ArgumentParser(
        description="SHAWPY Status Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=cfg["server"]["host"], help="Bind address")
    parser.add_argument("--port", type=int, default=cfg["server"]["port"], help="Bind port")
    parser.add_argument("--json", action="store_true", help="Respond with JSON instead of ASCII")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    server = StatusServer(
        host=args.host,
        port=args.port,
        max_clients=cfg["server"].get("max_clients", 8),
        json_mode=args.json,
        title=cfg["display"].get("title", "SHAWPY // STATUS"),
        width=cfg["display"].get("width", 42),
    )

    def _signal_handler(sig, frame):
        server.stop()

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_handler)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
