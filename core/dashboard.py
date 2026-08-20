"""
ASCII dashboard renderer for SHAWPY status.
Produces a clean fixed-width box that stays aligned.
"""

from __future__ import annotations

from .stats import SystemStats, GPUInfo


def _truncate(text: str, width: int) -> str:
    text = text.strip()
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def _line(label: str, value: str, inner: int = 38) -> str:
    """Build one content line: ║  LABEL  value... ║"""
    # label is fixed ~10 chars, then value fills the rest
    label_w = 10
    value_w = inner - label_w - 2  # spaces around
    lab = f"{label:<{label_w}}"
    val = _truncate(value, value_w)
    content = f"  {lab}{val}"
    # Pad to exact inner width
    content = f"{content:<{inner}}"
    return f"║{content}║"


def _blank(inner: int = 38) -> str:
    return f"║{' ' * inner}║"


def _sep(inner: int = 38) -> str:
    return f"╠{'═' * inner}╣"


def _bar(pct: float, width: int = 10) -> str:
    """Simple text progress bar."""
    pct = max(0.0, min(100.0, pct))
    filled = int(round((pct / 100) * width))
    return "█" * filled + "░" * (width - filled)


def render(stats: SystemStats, title: str = "SHAWPY // STATUS", width: int = 42) -> str:
    """
    Render a full status dashboard as a multi-line string.
    width is the total outer width including borders.
    """
    inner = width - 2  # inside the ║ ║
    if inner < 30:
        inner = 30
        width = inner + 2

    top = f"╔{'═' * inner}╗"
    title_line = f"║{title:^{inner}}║"
    bottom = f"╚{'═' * inner}╝"

    lines: list[str] = [
        "",
        top,
        title_line,
        _sep(inner),
        _line("HOST", stats.hostname, inner),
        _line("OS", stats.os_name, inner),
        _blank(inner),
    ]

    # CPU
    cpu_label = stats.cpu_name
    lines.append(_line("CPU", cpu_label, inner))
    if stats.cpu_cores:
        cpu_detail = f"{stats.cpu_percent:5.1f}%  {_bar(stats.cpu_percent)}  {stats.cpu_cores} thr"
        lines.append(_line("", cpu_detail, inner))

    # RAM
    ram_str = f"{stats.ram_used_gb:.1f}/{stats.ram_total_gb:.1f} GiB  ({stats.ram_percent:.0f}%)"
    lines.append(_line("RAM", ram_str, inner))
    lines.append(_line("", _bar(stats.ram_percent, 16), inner))

    # Disk
    if stats.disk_total_gb > 0:
        disk_str = f"{stats.disk_used_gb:.0f}/{stats.disk_total_gb:.0f} GiB  ({stats.disk_percent:.0f}%)"
        lines.append(_line("DISK", disk_str, inner))

    # GPU
    gpu: GPUInfo = stats.gpu
    if gpu.available:
        lines.append(_line("GPU", gpu.name, inner))
        gpu_detail = f"{gpu.util_pct:>3}%  TEMP {gpu.temp_c:>3}°C"
        lines.append(_line("", gpu_detail, inner))
        vram = f"{gpu.vram_used_mib} / {gpu.vram_total_mib} MiB"
        lines.append(_line("VRAM", vram, inner))
    else:
        lines.append(_line("GPU", "not detected", inner))

    lines.append(_blank(inner))
    lines.append(_line("UPTIME", stats.uptime, inner))
    lines.append(_blank(inner))
    lines.append(_line("STATUS", "● ONLINE", inner))
    lines.append(bottom)
    lines.append("")

    return "\n".join(lines)


def render_offline(error: str = "", title: str = "SHAWPY // STATUS", width: int = 42) -> str:
    inner = width - 2
    top = f"╔{'═' * inner}╗"
    title_line = f"║{title:^{inner}}║"
    bottom = f"╚{'═' * inner}╝"

    lines = [
        "",
        top,
        title_line,
        _sep(inner),
        _blank(inner),
        _line("NETWORK", "OFFLINE", inner),
        _line("SERVER", "UNREACHABLE", inner),
        _blank(inner),
    ]
    if error:
        lines.append(_line("ERROR", _truncate(error, inner - 14), inner))
        lines.append(_blank(inner))
    lines.append(bottom)
    lines.append("")
    return "\n".join(lines)
