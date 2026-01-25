# Web Frontend Development Guide

This document describes the new web frontend for AlongGPX and how it integrates with the existing infrastructure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Containers                            │
│                                                                      │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │   Frontend       │              │   Backend API    │             │
│  │   (React/Vite)   │──────────→   │   (Flask)        │             │
│  │   :3000          │              │   :5000          │             │
│  └──────────────────┘              └──────────────────┘             │
│                                            │                         │
│                                            ↓                         │
│                                    ┌────────────────┐                │
│                                    │ AlongGPX Core  │                │
│                                    │   Pipeline     │                │
│                                    └────────────────┘                │
│                                            │                         │
│                                            ↓                         │
│                                  ┌──────────────────┐               │
│                                  │   Overpass API   │               │
│                                  │   OSM Data       │               │
│                                  └──────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

## Frontend Structure

```
web/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app orchestrator
│   ├── App.css               # Layout styles
│   ├── index.css             # Global styles
│   ├── api.ts                # API client & types
│   └── components/
│       ├── UploadArea.tsx     # GPX file upload with drag-drop
│       ├── UploadArea.css
│       ├── SettingsForm.tsx   # Project settings & filters
│       ├── SettingsForm.css
│       ├── ProgressCard.tsx   # Real-time progress display
│       ├── ProgressCard.css
│       ├── ResultsPanel.tsx   # Results + download links
│       └── ResultsPanel.css
├── index.html                # HTML template
├── package.json              # Dependencies
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript config
└── Dockerfile                # Docker image definition
```

## Backend Integration

### New API Endpoints

**`GET /api/config`**
- Returns default configuration and available presets
- Used by frontend to populate dropdowns and initial values
- Response:
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
    "presets_detail": {
      "camp_basic": {
        "include": ["tourism=camp_site"],
        "exclude": ["tents=no"]
      }
    }
  }
  ```

**`POST /api/process`**
- Async start of GPX processing
- Returns immediately with a `job_id` for polling
- Request: multipart/form-data with file, settings, filters
- Response (HTTP 202):
  ```json
  {
    "job_id": "uuid-string",
    "status_url": "/api/status/uuid-string"
  }
  ```

**`GET /api/status/<job_id>`**
- Poll job progress
- Response:
  ```json
  {
    "id": "uuid",
    "state": "processing|completed|failed|queued",
    "percent": 45,
    "message": "Processing track...",
    "project_name": "MyProject",
    "created_at": "2026-01-25T10:30:45",
    "excel_file": "MyProject_20260125_103045.xlsx",
    "html_file": "MyProject_20260125_103045.html",
    "rows_count": 42,
    "track_length_km": 125.5,
    "error": null
  }
  ```

### Async Processing Implementation

The Flask app now:
1. Creates a job entry in `job_registry` on `/api/process` POST
2. Returns immediately with HTTP 202 + job_id
3. Spawns a background thread running `process_gpx_async()`
4. Updates job status as pipeline progresses
5. Frontend polls `/api/status/<job_id>` every 1 second

Thread-safe updates via `job_registry_lock` prevent race conditions.

## Frontend Workflow

### 1. **Idle Stage** (User uploads & configures)
   - Load config via `/api/config` → populate defaults
   - Accept GPX file via drag-drop
   - Adjust settings (radius, include/exclude filters, presets)
   - Click "Generate" button

### 2. **Processing Stage** (Async job running)
   - POST to `/api/process` → get job_id
   - Poll `/api/status/<job_id>` every 1s
   - Show progress bar + status message
   - Display summary stats when available

### 3. **Results Stage** (Job completed)
   - Show success card with POI count & track length
   - Button to open Folium map in new tab
   - Button to download Excel file
   - "Process Another Track" button to reset

### 4. **Error Stage** (Job failed)
   - Show error message from backend
   - "Try Again" button to reset

## Running Locally

### Option 1: Local Dev (npm + Flask side-by-side)

**Terminal 1 - Backend:**
```bash
cd /home/rik/AlongGPX
python3 docker/app.py
```
Flask listens on http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd /home/rik/AlongGPX/web
npm install
npm run dev
```
Vite listens on http://localhost:3000
Proxies `/api/*` to http://localhost:5000

### Option 2: Docker Compose (Production-like)

**Development with hot reload:**
```bash
cd /home/rik/AlongGPX/docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

**Production build:**
```bash
cd /home/rik/AlongGPX/docker
docker-compose up
```
- Frontend serves static build: http://localhost:3000
- Backend API: http://localhost:5000

## Styling & Design System

### CSS Variables (in `src/index.css`)
- **Colors**: primary, success, error, warning, background tiers, text tiers
- **Spacing**: xs (0.25rem) through 2xl (3rem)
- **Radii**: sm, md, lg
- **Shadows**: light shadow, large shadow
- **Typography**: font family, sizes sm-2xl

### Component Philosophy
- Minimal, functional design (no heavy UI libraries)
- Accessibility-first (proper semantic HTML, focus states)
- Mobile-responsive (CSS Grid + media queries)
- Smooth animations for state transitions
- Consistent spacing & typography via CSS vars

## Adding New Features

### Adding a Preset
1. Edit `presets.yaml` with new include/exclude filters
2. Restart backend or reload page → dropdown auto-populates

### Adding a Filter Type
1. Update `/api/config` response in `docker/app.py`
2. Add input field in `SettingsForm.tsx`
3. Pass via `/api/process` form data

### Custom Map Styling
1. Edit `core/folium_map.py`: marker colors, zoom, track line style
2. Redeploy

## Troubleshooting

### Frontend can't connect to API
- Check if Flask is running on port 5000
- Check browser DevTools Network tab for CORS errors
- In dev mode: Vite proxy in `vite.config.ts` should forward `/api` calls

### Docker networking issues
- Use service name (`app` instead of `localhost:5000`) in docker-compose
- Check `docker-compose logs -f app` for backend errors
- Ensure both services are in same network (default: yes)

### Job stuck in "processing"
- Check Flask logs: `docker-compose logs -f app`
- Long-running Overpass queries or dense regions slow things down
- Increase `batch_km` in config.yaml to reduce API calls

## Future Enhancements

- [ ] Real-time activity logs (WebSocket instead of polling)
- [ ] Job history & re-run capability
- [ ] Map preview before download (embed Folium viewer)
- [ ] User authentication & project management
- [ ] Batch processing (multiple GPX files)
- [ ] Advanced filter builder UI
- [ ] Dark mode toggle
