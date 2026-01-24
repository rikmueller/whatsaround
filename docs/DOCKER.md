# Docker Deployment Guide

Run AlongGPX as a containerized REST API with Docker and Docker Compose.

---

## Quick Start (2 minutes)

**Prerequisites:** Docker ≥ 20.10, Docker Compose ≥ 1.29

1. Start the container:
   ```bash
   cd docker
   docker-compose up -d
   ```

2. Verify it's running:
   ```bash
   curl http://localhost:5000/health
   ```
   Response: `{"status": "healthy", "service": "AlongGPX"}`

3. Upload and process a GPX file:
   ```bash
   curl -F "file=@../data/input/track.gpx" \
        -F "project_name=MyTrip" \
        -F "radius_km=5" \
        http://localhost:5000/api/process
   ```

Done! Excel and HTML map are saved to `../data/output/`.

---

## How It Works

AlongGPX runs a Flask web API in a Docker container. You upload GPX files and receive JSON responses with links to Excel and interactive Folium maps.

**Volume mounts (default):**
- `../data/input/` (read-only) ← GPX files for processing
- `../data/output/` (read-write) ← Generated Excel/HTML results

**Configuration hierarchy** (highest → lowest):
1. Web API form parameters (`-F "radius_km=10"`)
2. Environment variables (`.env` file)
3. `config.yaml` defaults

---

## API Reference

### Health Check
```bash
GET /health
```
Simple status endpoint for monitoring. Returns 200 if container is healthy.

### Process GPX File
```bash
POST /api/process
Content-Type: multipart/form-data
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | GPX file (*.gpx) |
| `project_name` | String | No | Output filename prefix (default: from config) |
| `radius_km` | Float | No | Search radius in km (default: 5) |
| `step_km` | Float | No | Distance between query points (default: 60% of radius) |
| `include` | String | No | Include filter, e.g., `tourism=camp_site` (repeatable) |
| `exclude` | String | No | Exclude filter, e.g., `tents=no` (repeatable) |

**Example:**
```bash
curl -F "file=@track.gpx" \
     -F "project_name=MyTrip" \
     -F "radius_km=5" \
     -F "include=tourism=camp_site" \
     -F "exclude=tents=no" \
     http://localhost:5000/api/process
```

**Response:**
```json
{
  "success": true,
  "excel_file": "MyTrip_20260124_120000.xlsx",
  "html_file": "MyTrip_20260124_120000.html",
  "excel_path": "/app/data/output/MyTrip_20260124_120000.xlsx",
  "html_path": "/app/data/output/MyTrip_20260124_120000.html",
  "rows_count": 42,
  "track_length_km": 125.5
}
```

---

## Configuration

Docker uses the same configuration as CLI. Set values via environment variables (highest priority), then `config.yaml` defaults.

### Method 1: .env File (Recommended)
Create `docker/.env`:
```bash
FLASK_ENV=production
ALONGGPX_RADIUS_KM=5
ALONGGPX_BATCH_KM=50
ALONGGPX_TIMEZONE=Europe/Berlin
```

### Method 2: docker-compose.yml
```yaml
services:
  alonggpx:
    environment:
      - ALONGGPX_RADIUS_KM=5
      - ALONGGPX_BATCH_KM=50
```

### Method 3: Mount config.yaml
```yaml
volumes:
  - ../config.yaml:/app/config.yaml:ro
```

**All environment variables:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `ALONGGPX_RADIUS_KM` | Search radius (km) | 5 |
| `ALONGGPX_STEP_KM` | Query point spacing | 60% of radius |
| `ALONGGPX_BATCH_KM` | Overpass batch size | 50 |
| `ALONGGPX_OVERPASS_RETRIES` | Retry attempts | 3 |
| `ALONGGPX_TIMEZONE` | Timestamp timezone | UTC |
| `FLASK_ENV` | Flask mode (production/development) | production |

See [QUICKSTART.md](QUICKSTART.md#configuration) for general configuration details.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port 5000 in use** | Change in docker-compose.yml: `ports: ["5001:5000"]` |
| **"Connection refused" on /api/process** | Wait 10s for health check; check logs: `docker-compose logs` |
| **Upload fails / "No such file or directory"** | Ensure GPX file exists in `../data/input/`; check volume mounts in docker-compose.yml |
| **No results from Overpass** | Verify filter syntax (`key=value`); test on [overpass-turbo.eu](https://overpass-turbo.eu/) |
| **Overpass API timeout** | Increase `ALONGGPX_BATCH_KM` to reduce query load; check https://overpass-api.de/ status |
| **Container won't start** | View logs: `docker logs alonggpx-web` (check for missing files or permission errors) |
| **Can't write output files** | Check that `../data/output/` directory exists and is writable |

---

## Viewing Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# With timestamps
docker-compose logs --timestamps
```

---

## Manual Build (Advanced)

If not using `docker-compose`, build and run manually:

```bash
cd docker
docker build -t alonggpx:latest ..

docker run -p 5000:5000 \
  -v "$(pwd)/../data/input:/app/data/input:ro" \
  -v "$(pwd)/../data/output:/app/data/output:rw" \
  -e ALONGGPX_RADIUS_KM=5 \
  alonggpx:latest
```

---

## Development & Testing

### Test Locally (No Docker)
```bash
# CLI mode
python3 cli/main.py --gpx-file ./data/input/track.gpx --radius-km 5

# Web API in development mode
export FLASK_ENV=development
python -m flask --app docker.app run --port 5000
```

### Debugging
Enable debug mode in docker-compose.yml:
```yaml
environment:
  - FLASK_ENV=development
```

Then restart: `docker-compose up -d --build`

---

## Production Deployment

### Use Gunicorn (Production Web Server)
Replace Flask's dev server with Gunicorn for concurrent request handling:

Edit `docker/Dockerfile`:
```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "docker.app:app"]
```

Rebuild: `docker-compose up -d --build`

### Reverse Proxy (Nginx)
For SSL/TLS and multiple replicas:

```nginx
upstream alonggpx {
    server localhost:5000;
}

server {
    listen 443 ssl;
    server_name gpx.example.com;
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location / {
        proxy_pass http://alonggpx;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }
}
```


---

## Architecture & Design

**Multi-stage Docker build:**
- Base stage: Installs dependencies, builds wheels
- Production stage: Copies only runtime (smaller image ~300MB)

**Security:**
- Runs as non-root user (`alonggpx`, UID 1000)
- Input directory is read-only
- No hardcoded credentials

**Health checks:**
- Polls `/health` endpoint every 30s
- Fails fast if container becomes unhealthy

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `Flask 3.0.0` | REST API framework |
| `gpxpy` | GPX parsing |
| `shapely` | Geometric operations |
| `pyproj` | Geodetic distance (WGS84 ellipsoid) |
| `requests` | HTTP to Overpass API |
| `folium` | Interactive map generation |
| `pandas` | DataFrame & Excel export |
| `python-dotenv` | Environment variable loading |

