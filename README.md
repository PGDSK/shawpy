# SHAWPY

A personal Linux-based engineering computing workspace and experimentation project — Python, networking, and system tooling, gradually growing alongside a civil and environmental engineering degree.

This is a learning project, not a product. Some of it is solid working code; some is an early sketch. The sections below try to be honest about which is which.

---

## What's actually working right now

### Status server + monitor (`04_network/`)

A small TCP client/server pair for checking a machine's live system stats (CPU, RAM, disk, GPU via `nvidia-smi`) from another machine on the network.

- `server.py` — runs on the machine you want to monitor. Threaded TCP server, line-based protocol.
- `monitor.py` — polls a running server and renders a live ASCII dashboard.
- `status.py` — one-shot local status print, no server needed.
- `core/` — shared modules: `config.py` (config loading + env var overrides), `stats.py` (system metrics collection, uses `psutil` when available), `dashboard.py` (ASCII rendering).
- `config.json` — server/monitor/display defaults.

Protocol (plain text over TCP):

| Client sends | Server replies |
|---|---|
| `STATUS` | ASCII dashboard, or JSON with `--json` |
| `PING` | `PONG` |
| `QUIT` | `goodbye` |

```bash
cd 04_network

python server.py                     # on the machine to monitor
python server.py --json -v           # JSON responses, verbose logging

python monitor.py                    # on the watching machine
python monitor.py --server 192.168.1.50 --refresh 1

python status.py                     # one-shot, no networking involved
```

Defaults live in `04_network/config.json` and can be overridden with `SHAWPY_HOST`, `SHAWPY_PORT`, `SHAWPY_MONITOR_SERVER`, or CLI flags.

### Mode scripts (`03_scripts/`)

Bash scripts that switch power profile and KDE Activity for `gaming` / `chill` / `workstation` / `server` modes:

```bash
chmod +x 03_scripts/*.sh
./03_scripts/gaming.sh
```

These are tied to one specific KDE/Nobara setup — they call `qdbus`, `kscreen-doctor`, and `powerprofilesctl` with hard-coded Activity UUIDs, so they won't do anything useful on a different machine without editing those UUIDs first. Kept as-is because they're genuine project history, not because they're portable.

### Tools (`01_tools/`)

- `calc.py` — a simple BMI calculator. Not an engineering tool, just an early scripting exercise kept for the record.

---

## Install

```bash
# Python 3.10+
pip install -r requirements.txt
```

`psutil` is the only dependency, used for RAM/CPU/disk stats in `04_network`. Optional: NVIDIA drivers so GPU stats appear via `nvidia-smi`.

---

## Repository layout

```
shawpy/
├── 01_tools/       # small standalone scripts (calc.py)
├── 03_scripts/     # Linux mode-switching scripts (+ 03_scripts/linux/, currently a duplicate copy)
├── 04_network/     # TCP status server, monitor, one-shot status, shared core/ modules
├── requirements.txt
└── README.md
```

This is what actually exists today, not a target structure. New material gets added alongside it rather than by renaming or reshuffling what's here.

---

## Linux only

Developed and tested on Linux. No Windows or macOS support is planned — no `.bat`/PowerShell launchers, no cross-platform abstractions added purely for portability.

---

## Where this is heading

SHAWPY is meant to grow alongside my degree rather than toward a fixed spec. Rough direction, not a commitment:

- **Mathematics** — small experiments from multivariable calculus: surfaces, contour plots, eventually gradients.
- **Engineering mechanics** — statics problems (beam reactions first, trusses later), checked against hand calculations.
- **Engineering project appraisal** — NPV / benefit-cost ratio / payback calculations from JSON or CSV input.
- **GIS / civil engineering** — terrain, slope, and spatial computing experiments, once there's a concrete reason to add them.
- **Networking** — possibly extending the existing TCP protocol so the server can run these computations remotely, but only after each module already works well on its own.

None of the above exists yet. This is a direction, not a feature list.

---

## Notes

- This is a personal learning project and a record of how coursework concepts turn into working code — not production software.
- `04_network/monitor.py.save` is a stray editor backup currently sitting in the repo; noting it here rather than silently removing it.
- `03_scripts/` and `03_scripts/linux/` currently hold duplicate copies of the same scripts — noted, not yet cleaned up.
