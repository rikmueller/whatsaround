# Quick Start Guide

Get AlongGPX running in 5 minutes. Choose your path: **CLI** (local machine) or **Docker** (web API).

---

## Prerequisites

| Mode | Requirement | Check |
|------|-------------|-------|
| CLI | Python 3.8+ | `python3 --version` |
| Docker | Docker + Docker Compose | `docker --version` |

---

## Path 1: CLI (Local Machine)

### Step 1: Install
```bash
cd AlongGPX
pip install -r requirements-base.txt
```

### Step 2: Run (First Time)
```bash
python3 cli/main.py --preset camp_basic
```

Results are in `data/output/`.

### Step 3: Customize (Optional)
```bash
# Different search radius
python3 cli/main.py --radius-km 10 --preset camp_basic

# Multiple filters
python3 cli/main.py \
  --preset camp_basic \
  --include amenity=drinking_water \
  --include amenity=shelter \
  --project-name MyTrip
```

See `python3 cli/main.py --help` for all options.

---

## Path 2: Docker (Web API)

### Step 1: Start Container
```bash
cd docker
docker-compose up -d
```

### Step 2: Verify
```bash
curl http://localhost:5000/health
# Response: {"status": "healthy", "service": "AlongGPX"}
```

### Step 3: Process GPX
```bash
curl -F "file=@../data/input/track.gpx" \
     -F "project_name=MyTrip" \
     -F "radius_km=5" \
     http://localhost:5000/api/process
```

Results are in `data/output/`.

See [DOCKER.md](DOCKER.md) for full API reference and configuration.

---

## Available Presets

Use `--preset` to quickly search for common POI types:

```bash
--preset camp_basic        # Campsites (tents allowed)
--preset accommodation     # Hotels, B&Bs, guest houses
--preset drinking_water    # Water sources
--preset shelters          # Emergency shelters
```

List all presets and create custom ones in [presets.yaml](../presets.yaml).

---

## Configuration

**For persistent settings**, edit [config.yaml](../config.yaml) in the repo root.

**For one-time overrides**, use CLI arguments (see `--help`) or environment variables:

```bash
export ALONGGPX_RADIUS_KM=8
export ALONGGPX_TIMEZONE=Europe/Berlin
python3 cli/main.py --preset camp_basic
```

**Priority (high → low):** CLI args > env vars > config.yaml

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `No such file or directory: cli/main.py` | Run from repo root: `cd AlongGPX` |
| No results found | Check filter syntax (`key=value`) and verify data at [overpass-turbo.eu](https://overpass-turbo.eu/) |
| Docker won't start | `docker system prune -f` then retry |
| Port 5000 in use | Edit `docker/docker-compose.yml`: `ports: ["5001:5000"]` |

For Docker-specific issues, see [DOCKER.md](DOCKER.md#troubleshooting).

---

## Next: Configure & Explore

- **Edit defaults:** [config.yaml](../config.yaml)
- **Add GPX files:** `data/input/` folder
- **Create presets:** [presets.yaml](../presets.yaml)
- **Web API?** → [DOCKER.md](DOCKER.md)
