# Configuration Migration Guide

## Overview

AlongGPX configuration has been restructured to separate CLI and Docker concerns. The old unified `config/config.yaml` file has been replaced with environment-based configuration using `.env` files.

## What Changed

### ❌ Removed Files
- `config/config.yaml` - Replaced by `.env` files
- `config/.env` - Split into `cli/.env`, `docker/.env`, and `web/.env`
- `core/config.py` functions (`load_yaml_config`, `load_env_config`, `merge_env_into_config`) - Replaced by simpler env loading

### ✅ New Files
- **`cli/.env`** - CLI configuration (source of truth for CLI tool)
- **`cli/.env.example`** - Template with all CLI variables documented
- **`docker/.env`** - Docker configuration (used by docker-compose)
- **`docker/.env.example`** - Template with all Docker variables documented
- **`web/.env`** - Frontend dev server configuration
- **`web/.env.example`** - Template for frontend variables

### 📝 Modified Files
- **`backend/app.py`** - Config loaded once at startup from env vars only (no YAML)
- **`cli/main.py`** - Loads from `cli/.env`, overridable by CLI args
- **`core/cli.py`** - Removed `--config` argument (no longer needed)
- **`docker/docker-compose.yml`** - Uses `env_file: .env`
- **`docker/Dockerfile`** - No longer copies `config/` directory (only `config/presets.yaml`)
- **`web/vite.config.ts`** - Reads from `web/.env` instead of `config/.env`

### 🔄 Moved Files
- **`config/presets.yaml`** → **`data/presets.yaml`** - Moved to data/ directory (still shared between CLI and Docker)

---

## Migration Steps

### For CLI Users

1. **Copy template to create your config:**
   ```bash
   cp cli/.env.example cli/.env
   ```

2. **Edit `cli/.env` with your settings:**
   ```bash
   ALONGGPX_PROJECT_NAME=MyProject
   ALONGGPX_GPX_FILE=../data/input/myroute.gpx
   ALONGGPX_RADIUS_KM=10
   # ... etc
   ```

3. **Old CLI command:**
   ```bash
   python cli/main.py --config config/config.yaml --radius-km 10
   ```
   
   **New CLI command:**
   ```bash
   python cli/main.py --radius-km 10
   ```
   
   Note: `--config` argument removed. All config comes from `cli/.env` (or CLI args override).

### For Docker Users

1. **Copy template to create your config:**
   ```bash
   cp docker/.env.example docker/.env
   ```

2. **Edit `docker/.env` with your settings:**
   ```bash
   FLASK_ENV=production
   ALONGGPX_PROJECT_NAME=DockerProject
   ALONGGPX_RADIUS_KM=5
   # ... etc
   ```

3. **Start Docker (same command as before):**
   ```bash
   cd docker
   docker-compose up -d
   ```
   
   Docker will automatically load variables from `docker/.env`.

### For Frontend Developers

1. **Copy template (if needed):**
   ```bash
   cp web/.env.example web/.env
   ```

2. **Edit `web/.env` for your dev environment:**
   ```bash
   ALONGGPX_HOSTNAME=localhost  # or your Docker host
   ```

3. **Start dev server (same as before):**
   ```bash
   cd web
   npm run dev
   ```

---

## Configuration Mapping

### Old config.yaml → New .env Variables

| Old (config.yaml)              | New (.env variable)              | Scope       |
|--------------------------------|----------------------------------|-------------|
| `project.name`                 | `ALONGGPX_PROJECT_NAME`         | CLI, Docker |
| `project.output_path`          | `ALONGGPX_OUTPUT_PATH`          | CLI, Docker |
| `project.timezone`             | `ALONGGPX_TIMEZONE`             | CLI, Docker |
| `input.gpx_file`               | `ALONGGPX_GPX_FILE`             | CLI only    |
| `search.radius_km`             | `ALONGGPX_RADIUS_KM`            | CLI, Docker |
| `search.step_km`               | `ALONGGPX_STEP_KM`              | CLI, Docker |
| N/A (new)                      | `ALONGGPX_PRESETS`              | CLI, Docker |
| `search.include`               | `ALONGGPX_SEARCH_INCLUDE`       | CLI, Docker |
| `search.exclude`               | `ALONGGPX_SEARCH_EXCLUDE`       | CLI, Docker |
| `overpass.retries`             | `ALONGGPX_OVERPASS_RETRIES`     | CLI, Docker |
| `overpass.batch_km`            | `ALONGGPX_BATCH_KM`             | CLI, Docker |
| `overpass.servers`             | `ALONGGPX_OVERPASS_SERVERS`     | CLI, Docker |
| `map.track_color`              | `ALONGGPX_TRACK_COLOR`          | CLI, Docker |
| `map.default_marker_color`     | `ALONGGPX_DEFAULT_MARKER_COLOR` | CLI, Docker |
| `map.marker_color_palette`     | `ALONGGPX_MARKER_COLOR_PALETTE` | CLI, Docker |
| `cleanup.interval_seconds`     | `ALONGGPX_CLEANUP_INTERVAL_SECONDS` | Docker only |
| `cleanup.job_ttl_seconds`      | `ALONGGPX_JOB_TTL_SECONDS`      | Docker only |
| `cleanup.temp_file_max_age_seconds` | `ALONGGPX_TEMP_FILE_MAX_AGE_SECONDS` | Docker only |
| `cleanup.output_retention_days` | `ALONGGPX_OUTPUT_RETENTION_DAYS` | Docker only |

### List Formatting
- **Old:** YAML arrays
- **New:** Semicolon-separated strings
  ```bash
  # Examples:
  ALONGGPX_PRESETS=shelters;drinking_water
  ALONGGPX_SEARCH_INCLUDE=tourism=camp_site;amenity=shelter
  ALONGGPX_OVERPASS_SERVERS=https://server1.com;https://server2.com
  ```

---

## Configuration Precedence

### CLI
```
CLI arguments > cli/.env > defaults
```

Example:
```bash
# In cli/.env:
ALONGGPX_RADIUS_KM=5

# Command line:
python cli/main.py --radius-km 10

# Result: Uses 10 (CLI arg wins)
```

### Docker
```
docker-compose environment: > docker/.env > defaults
```

### Backend (Web API)
```
Environment variables > defaults
```

---

## Advantages of New System

✅ **Docker Standard**: Uses standard Docker `.env` files and `env_file` directive  
✅ **Simpler**: No complex YAML merging logic, just read env vars  
✅ **Cleaner Separation**: CLI and Docker configs are independent  
✅ **Better Performance**: Backend loads config once at startup (not 6 times per request)  
✅ **GHCR Compatible**: No runtime dependency on config.yaml (everything in env vars)  
✅ **Environment-Specific**: Easy to have dev/staging/prod configs  

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
**Solution:** Install python-dotenv (already in requirements)
```bash
pip install python-dotenv
```

### "Configuration loaded from environment variables" shows wrong values
**Solution:** Check your `.env` file location and syntax:
- CLI: `cli/.env` must exist
- Docker: `docker/.env` must exist
- Syntax: `KEY=value` (no quotes needed, no spaces around `=`)

### CLI can't find presets.yaml
**Solution:** Set correct path in `cli/.env`:
```bash
ALONGGPX_PRESETS_FILE=data/presets.yaml
```

### Docker can't find presets.yaml
**Solution:** Ensure volume mount in docker-compose.yml:
```yaml
volumes:
  - ../data/presets.yaml:/app/data/presets.yaml:ro
```

---

## Breaking Changes

This is a **breaking change** (v2.0.0). Users must:
1. Copy `.env.example` files to create `.env` files
2. Transfer their old `config.yaml` settings to new `.env` format
3. Update any automation/scripts that referenced `config.yaml`

## Backward Compatibility

**None.** The old config.yaml system is completely removed. This was necessary to:
- Eliminate technical debt
- Align with Docker best practices
- Simplify codebase for future maintenance
- Fix GHCR image deployment issues
