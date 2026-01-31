# AlongGPX Docker Production Configuration

This directory contains configuration for **Docker production deployment** with pre-built images and Nginx reverse proxy.

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cp config/docker-prod/.env.example config/docker-prod/.env
   ```

2. **Edit `config/docker-prod/.env`** with your preferences:
   - Set `ALONGGPX_PROJECT_NAME` for default project naming
   - Adjust `ALONGGPX_RADIUS_KM` for default search radius
   - Configure default filters or presets (optional)

3. **Build and start services:**
   ```bash
   cd config/docker-prod
   docker compose up -d
   ```

4. **Access the application:** http://localhost:3000

## Architecture

```
nginx:3000 (frontend static files + reverse proxy)
    ↓
backend:5000 (Flask API for GPX processing)
```

## Services

### nginx (port 3000)
- Serves built React frontend (static HTML/JS/CSS)
- Reverse proxies `/api/*` to Flask backend
- Reverse proxies `/socket.io/*` for real-time updates

### backend (port 5000, internal)
- Flask API for GPX processing
- Processes uploaded GPX files
- Generates Excel and HTML outputs

## Volumes

Data is persisted in these host directories:
- `../../data/input` → `/app/data/input` (read-only)
- `../../data/output` → `/app/data/output` (read-write)
- `../../data/presets.yaml` → `/app/data/presets.yaml` (read-only)

## Configuration

### User Settings (in .env)
Simple settings exposed to users via `.env` file.

### Advanced Settings (in docker-compose.yml)
Hardcoded with sensible defaults:
- Overpass API servers and retry logic
- Background cleanup intervals
- Map colors and visualization
- File retention policies

**To customize advanced settings:** Edit `docker-compose.yml` environment section.

## Logs

View logs for debugging:
```bash
docker compose logs -f          # All services
docker compose logs -f backend  # Backend only
docker compose logs -f nginx    # Nginx only
```

## Updating

Pull latest images and restart:
```bash
docker compose pull
docker compose up -d
```

Rebuild from source:
```bash
docker compose up -d --build
```

## Data Management

### Cleanup Old Outputs
Results accumulate in `data/output/`. The backend automatically deletes files older than 10 days (configurable via `ALONGGPX_OUTPUT_RETENTION_DAYS` in docker-compose.yml).

Manual cleanup:
```bash
find ../../data/output -type f -mtime +30 -delete
```

## Troubleshooting

### Port 3000 already in use
Change the published port in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"  # Access via http://localhost:8080
```

### Backend processing fails
Check backend logs:
```bash
docker compose logs backend
```

### Cannot upload files
Check volume permissions:
```bash
ls -la ../../data/output
chmod 777 ../../data/output  # If needed
```

## See Also

- [../../deployment/README.md](../../deployment/README.md) - Dockerfile details
- [../../docs/quickstart-docker.md](../../docs/quickstart-docker.md) - Detailed Docker guide
- [docker-compose.yml](./docker-compose.yml) - Service configuration
