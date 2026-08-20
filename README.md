# SHAWPY

Personal system-status dashboard and mode switcher.  
Works on **Linux**.

---

## Install

```bash
# Python 3.10+ required
pip install -r requirements.txt
```

Optional but recommended: **NVIDIA drivers** so GPU stats appear via `nvidia-smi`.

---

## Status Server + Monitor

### Start the server (machine to monitor)

```bash
python server.py
# or on Windows: double-click run_server.bat
```

Options:

| Flag | Description |
|------|-------------|
| `--host 0.0.0.0` | Bind address (default from config) |
| `--port 8000` | Port |
| `--json` | Return machine-readable JSON instead of ASCII |
| `-v` | Verbose logging |

### Start the monitor (any machine)

Edit `config.json` → `monitor.server` (or pass flags):

```bash
python monitor.py
python monitor.py --server 192.168.1.50 --refresh 1
# or: run_monitor.bat
```

| Flag | Description |
|------|-------------|
| `-s / --server` | Host or IP of the status server |
| `-p / --port` | Port |
| `-r / --refresh` | Seconds between polls |
| `-t / --timeout` | Connect timeout |

### Config file (`config.json`)

```json
{
  "server": { "host": "0.0.0.0", "port": 8000 },
  "monitor": { "server": "100.124.10.41", "port": 8000, "refresh_seconds": 2 },
  "display": { "title": "SHAWPY // STATUS", "width": 42 }
}
```

Environment overrides: `SHAWPY_HOST`, `SHAWPY_PORT`, `SHAWPY_MONITOR_SERVER`.

Firewall: allow **TCP 8000** inbound on the server machine if monitoring remotely.

---

## Mode Scripts

### Windows (PowerShell)

```powershell
# One-time
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

cd scripts\ 
.\mode.ps1 gaming
.\mode.ps1 chill
.\mode.ps1 workstation
.\mode.ps1 server      # keeps the PC awake
```

| Mode | Power plan | Brightness |
|------|------------|------------|
| `chill` | Power saver | 40% |
| `gaming` | High performance | 100% |
| `workstation` | Balanced | 80% |
| `server` | Power saver + sleep inhibited | — |

Brightness only works on supported laptop panels.

### Linux (original KDE / Nobara scripts)

```bash
chmod +x scripts/linux/*.sh
./scripts/linux/gaming.sh
./scripts/linux/chill.sh
# etc.
```

These use KDE Activities, `kscreen-doctor`, `powerprofilesctl`, and hard-coded activity UUIDs — they only work on the machine they were written for.

---

## Project Layout

```
shawpy-main/
├── server.py              # Status TCP server
├── monitor.py             # Live dashboard client
├── config.json            # Defaults (edit me)
├── requirements.txt
├── run_server.bat         # Windows convenience launchers
├── run_monitor.bat
├── core/
│   ├── config.py          # Config loader + env overrides
│   ├── stats.py           # Cross-platform system metrics
│   └── dashboard.py       # ASCII box renderer
├── scripts/
│   ├── linux/             # Original KDE shell scripts
│   └──  /           # PowerShell mode switcher
└── tools/
    └── calc.py            # BMI calculator
```

---

## Protocol

Simple line-based TCP protocol on the configured port:

| Client sends | Server replies |
|--------------|----------------|
| `STATUS` | ASCII dashboard (or JSON with `--json`) |
| `PING` | `PONG` |
| `QUIT` | `goodbye` |

---

## Notes

- `psutil` is required for accurate RAM, CPU %, disk, and uptime on Windows.
- Without `psutil` the server still runs but many fields will be empty/zero.
- Multi-GPU: first GPU reported by `nvidia-smi` is shown.
- The server is multi-client (threaded) and handles graceful Ctrl+C shutdown.
