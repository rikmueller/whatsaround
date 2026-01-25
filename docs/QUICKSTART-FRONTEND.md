# AlongGPX Web Frontend - Quick Start Guide

This guide covers setting up and running the new web frontend.

## What's New?

✨ **Complete web interface for AlongGPX** featuring:
- 📂 Drag-and-drop GPX file upload
- ⚙️ Configurable search radius, presets, and filters
- ⏳ Real-time progress tracking during processing
- 🗺️ Interactive Folium map viewer
- 📊 Excel export download
- 🎨 Sleek, modern UI with responsive design

## Quick Start

### Option 1: Local Development (Fastest for testing)

**Requirements:**
- Python 3.10+ with Flask
- Node.js 18+ with npm
- Your existing AlongGPX setup

**Terminal 1 - Start Flask backend:**
```bash
cd /home/rik/AlongGPX

# First time: install web dependencies
pip install -r docker/requirements-web.txt

# Start Flask
python3 docker/app.py
# Output: Running on http://0.0.0.0:5000
```

**Terminal 2 - Start React frontend:**
```bash
cd /home/rik/AlongGPX/web
npm install  # First time only
npm run dev
# Output: Local:   http://localhost:3000
```

**Open browser:** http://localhost:3000

---

### Option 2: Docker Compose (Production-like setup)

**Requirements:**
- Docker & Docker Compose
- `cd /home/rik/AlongGPX/docker`

**Development mode (with hot reload):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

**Production mode:**
```bash
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

Both services will start automatically. Wait ~30 seconds for frontend to build.

---

## Usage Walkthrough

### 1. **Upload GPX File**
   - Drag and drop a .gpx file onto the upload area, or click to browse
   - File will appear with a ✓ checkmark

### 2. **Configure Settings**
   - **Project Name**: Name for output files
   - **Search Radius**: Distance around each track point (1-50 km)
   - **Presets**: Quick-select filter profiles (camp_basic, drinking_water, etc.)
   - **Include Filters**: OSM tags to search for (e.g., `tourism=camp_site`)
   - **Exclude Filters**: OSM tags to exclude (e.g., `tents=no`)

### 3. **Start Processing**
   - Click **🚀 Generate** button
   - Processing begins immediately

### 4. **Monitor Progress**
   - See real-time progress bar (0-100%)
   - Current status message updates
   - POI count appears when available

### 5. **View Results**
   - **Open Map**: View all POIs on interactive Folium map
   - **Download Excel**: Get detailed data table with all POI info
   - **Process Another**: Start over with a new track

---

## Architecture

```
┌─────────────────────────────────────┐
│   Frontend (React/Vite)             │
│   http://localhost:3000             │
└─────────────┬───────────────────────┘
              │
              │ HTTP/API calls
              │
┌─────────────▼───────────────────────┐
│   Backend (Flask)                   │
│   http://localhost:5000             │
│                                     │
│   /api/config        - Get settings │
│   /api/process       - Start job    │
│   /api/status/{id}   - Check status │
│   /api/download/*    - Get files    │
└─────────────┬───────────────────────┘
              │
              │ Overpass queries
              │
┌─────────────▼───────────────────────┐
│   AlongGPX Core Pipeline            │
│   - GPX parsing                     │
│   - Overpass API calls              │
│   - Filter + distance calc          │
│   - Excel + Folium export           │
└─────────────────────────────────────┘
```

---

## API Reference

### GET /api/config
Returns configuration defaults and available presets.

**Response:**
```json
{
  "defaults": {
    "project_name": "MyProject",
    "radius_km": 5,
    "step_km": null,
    "include": ["tourism=camp_site"],
    "exclude": ["tents=no"]
  },
  "presets": ["camp_basic", "drinking_water", ...],
  "presets_detail": { ... }
}
```

### POST /api/process
Start asynchronous processing of a GPX file.

**Request:**
- Multipart form-data
- `file`: GPX file
- `project_name`: Project name (string)
- `radius_km`: Search radius (number)
- `include`: Include filters (repeated field)
- `exclude`: Exclude filters (repeated field)
- `preset`: Preset names (repeated field)

**Response (HTTP 202):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_url": "/api/status/550e8400-e29b-41d4-a716-446655440000"
}
```

### GET /api/status/{job_id}
Poll job progress.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "processing",
  "percent": 45,
  "message": "Querying Overpass API...",
  "project_name": "MyProject",
  "created_at": "2026-01-25T10:30:45",
  "excel_file": "MyProject_20260125_103045.xlsx",
  "html_file": "MyProject_20260125_103045.html",
  "rows_count": 42,
  "track_length_km": 125.5,
  "error": null
}
```

**States:**
- `queued`: Waiting to start
- `processing`: Currently running
- `completed`: Done! Results ready
- `failed`: Error occurred (see `error` field)

---

## Troubleshooting

### "ModuleNotFoundError" (Local Flask)
1. Install web dependencies: `pip install -r docker/requirements-web.txt`
2. For CLI-only: `pip install -r cli/requirements-cli.txt`

### "Can't connect to API" (Frontend)
1. Check Flask is running: `curl http://localhost:5000/health`
2. Check port 5000 is not in use: `lsof -i :5000`
3. In dev mode, Vite should proxy `/api` calls automatically

### "Frontend won't load" (Blank page)
1. Check Vite is running: `npm run dev` in `/web` directory
2. Check port 3000 is free: `lsof -i :3000`
3. Check browser console (F12) for errors

### "Job stuck in processing"
1. Check Flask logs for errors: `docker-compose logs -f app`
2. Large GPX files or dense regions may take time
3. Increase `batch_km` in `config.yaml` to speed up Overpass queries

### Docker build fails
1. Ensure Node.js 18+ and Python 3.10+: `node -v`, `python3 --version`
2. Check Docker daemon is running: `docker ps`
3. Force rebuild: `docker-compose build --no-cache`

### File permissions error
1. Ensure `data/output/` directory exists and is writable
2. Fix permissions: `chmod 755 data/output`

---

## File Structure

```
AlongGPX/
├── cli/                    # CLI entrypoint
├── core/                   # Pipeline modules
├── docker/                 # Backend (Flask)
│   ├── app.py             # NEW: Job tracking + async processing
│   └── docker-compose.yml  # UPDATED: Frontend service added
├── web/                    # NEW: Frontend (React/Vite)
│   ├── src/               # Source code
│   │   ├── App.tsx        # Main orchestrator
│   │   ├── api.ts         # API client
│   │   └── components/    # UI components
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── docs/                   # Documentation
│   ├── FRONTEND.md        # NEW: Detailed frontend guide
│   └── ...
└── data/
    ├── input/             # GPX files
    └── output/            # Excel + HTML results
```

---

## Development Notes

### Adding a New Preset
1. Edit `presets.yaml` in repo root
2. Restart Flask or reload frontend → auto-appears in Presets dropdown

### Customizing UI
- Edit `web/src/components/*.tsx` for layout
- Edit `web/src/components/*.css` for styling
- CSS variables defined in `web/src/index.css`

### Extending API
- Add endpoints to `docker/app.py`
- Add API client methods to `web/src/api.ts`
- Create or update components as needed

---

## Next Steps

1. ✅ **Run locally** - Test with your GPX files
2. 📋 **Review UI** - Provide feedback on the interface
3. 🔧 **Customize** - Add/modify presets, adjust styling
4. 🚀 **Deploy** - Use Docker for production hosting
5. 🛡️ **Secure** - Add authentication, rate limiting as needed

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f` (for Docker mode)
2. Test API directly: `curl http://localhost:5000/health`
3. Check browser console (F12) for frontend errors
4. Review `docs/FRONTEND.md` for detailed technical info

Happy trail mapping! 🗺️
