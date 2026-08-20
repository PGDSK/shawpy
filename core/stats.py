"""
System statistics collection.
Cross-platform (Windows + Linux). Uses psutil when available.
"""

from __future__ import annotations

import platform
import socket
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class GPUInfo:
    name: str = "N/A"
    temp_c: str = "?"
    util_pct: str = "?"
    vram_used_mib: str = "?"
    vram_total_mib: str = "?"
    available: bool = False


@dataclass
class SystemStats:
    hostname: str = ""
    os_name: str = ""
    cpu_name: str = ""
    cpu_percent: float = 0.0
    cpu_cores: int = 0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    ram_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_percent: float = 0.0
    uptime: str = "unknown"
    gpu: GPUInfo = field(default_factory=GPUInfo)
    collected_at: datetime = field(default_factory=datetime.now)


def _run(cmd: list[str], timeout: float = 3.0) -> Optional[str]:
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            text=True,
        )
        return out.strip()
    except Exception:
        return None


def get_hostname() -> str:
    return socket.gethostname()


def get_os_name() -> str:
    system = platform.system()
    if system == "Windows":
        # e.g. "Windows-10-10.0.19045-SP0" → cleaner
        release = platform.release()
        return f"Windows {release}"
    if system == "Linux":
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except OSError:
            pass
        return "Linux"
    return system or "Unknown"


def get_cpu_name() -> str:
    system = platform.system()
    if system == "Windows":
        out = _run(["wmic", "cpu", "get", "Name"])
        if out:
            lines = [ln.strip() for ln in out.splitlines() if ln.strip() and ln.strip().lower() != "name"]
            if lines:
                return lines[0]
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
    # Fallback
    return platform.processor() or "Unknown CPU"


def get_cpu_percent() -> float:
    if HAS_PSUTIL:
        # Non-blocking: first call may return 0.0, so sample briefly
        return psutil.cpu_percent(interval=0.15)
    return 0.0


def get_cpu_cores() -> int:
    if HAS_PSUTIL:
        return psutil.cpu_count(logical=True) or 0
    return 0


def get_ram() -> tuple[float, float, float]:
    """Returns (used_gb, total_gb, percent)."""
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        return (
            mem.used / (1024 ** 3),
            mem.total / (1024 ** 3),
            mem.percent,
        )
    # Linux fallback
    if platform.system() != "Windows":
        out = _run(["free", "-b"])
        if out:
            try:
                parts = out.splitlines()[1].split()
                total = int(parts[1])
                used = int(parts[2])
                return used / (1024 ** 3), total / (1024 ** 3), (used / total) * 100
            except (IndexError, ValueError, ZeroDivisionError):
                pass
    return 0.0, 0.0, 0.0


def get_disk(path: str = "/") -> tuple[float, float, float]:
    """Returns (used_gb, total_gb, percent). On Windows uses C:\\."""
    if platform.system() == "Windows":
        path = "C:\\"
    if HAS_PSUTIL:
        try:
            usage = psutil.disk_usage(path)
            return (
                usage.used / (1024 ** 3),
                usage.total / (1024 ** 3),
                usage.percent,
            )
        except Exception:
            pass
    return 0.0, 0.0, 0.0


def get_uptime() -> str:
    if HAS_PSUTIL:
        boot = datetime.fromtimestamp(psutil.boot_time())
        delta = datetime.now() - boot
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes = rem // 60
        parts: list[str] = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    if platform.system() != "Windows":
        out = _run(["uptime", "-p"])
        if out:
            return out.replace("up ", "")
    return "unknown"


def get_gpu() -> GPUInfo:
    """Query nvidia-smi (works on Windows and Linux with NVIDIA drivers)."""
    out = _run([
        "nvidia-smi",
        "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ])
    if not out:
        return GPUInfo()

    # Handle multi-GPU: take first line
    line = out.splitlines()[0]
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 5:
        return GPUInfo()

    return GPUInfo(
        name=parts[0],
        temp_c=parts[1],
        util_pct=parts[2],
        vram_used_mib=parts[3],
        vram_total_mib=parts[4],
        available=True,
    )


def collect() -> SystemStats:
    """Gather a full snapshot of system stats."""
    used_gb, total_gb, ram_pct = get_ram()
    disk_used, disk_total, disk_pct = get_disk()

    return SystemStats(
        hostname=get_hostname(),
        os_name=get_os_name(),
        cpu_name=get_cpu_name(),
        cpu_percent=get_cpu_percent(),
        cpu_cores=get_cpu_cores(),
        ram_used_gb=used_gb,
        ram_total_gb=total_gb,
        ram_percent=ram_pct,
        disk_used_gb=disk_used,
        disk_total_gb=disk_total,
        disk_percent=disk_pct,
        uptime=get_uptime(),
        gpu=get_gpu(),
        collected_at=datetime.now(),
    )
