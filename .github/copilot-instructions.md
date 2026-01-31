# AlongGPX AI Coding Instructions

## Project Overview
AlongGPX finds OpenStreetMap POIs along GPX tracks using Overpass API queries, then exports results to Excel and interactive Folium maps. Core use case: trip planning (e.g., finding campsites/water/shelters along a bikepacking route).

**Three Interfaces:**
1. **Web UI** (React + TypeScript) - Modern browser-based interface with real-time progress
2. **CLI** (Python) - Command-line tool for batch processing and automation
3. **REST API** (Flask) - Backend for web UI, also usable standalone

## Architecture & Data Flow

### Backend Pipeline (Shared by all interfaces)
Located in `backend/core/` directory - reusable modules called by CLI and web API:

1. **Presets**: Load [data/presets.yaml](../data/presets.yaml) → apply to filters ([presets.py](../backend/core/presets.py))
2. **GPX**: Parse GPX → geodesic distance calculations with `pyproj.Geod(ellps="WGS84")` ([gpx_processing.py](../backend/core/gpx_processing.py))
3. **Overpass**: Batched queries along track with configurable `batch_km` ([overpass.py](../backend/core/overpass.py))
4. **Filter**: Include/exclude OSM tags → geodesic distance to track ([filtering.py](../backend/core/filtering.py))
5. **Export**: DataFrame → Excel + Folium map with color-coded markers ([export.py](../backend/core/export.py), [folium_map.py](../backend/core/folium_map.py))

Entry point: `cli.main.run_pipeline()` - returns dict with paths and metadata

### Frontend Architecture (React/TypeScript)
Modern map-first single-page application with continuous visual feedback:

**Core Files:**
- [frontend/src/DevApp.tsx](../frontend/src/DevApp.tsx) - Main orchestrator (stage management: idle → uploaded → processing → completed/error)
- [frontend/src/api.ts](../frontend/src/api.ts) - Typed API client with axios
- [frontend/src/components/](../frontend/src/components/) - Reusable UI components
- [frontend/src/hooks/](../frontend/src/hooks/) - Custom React hooks

**Key Components:**
- `BrandingHeader` - Glassmorphic header with branding and modern styling
- `SettingsSheet` - Collapsible settings sidebar (mobile-responsive with smooth animations)
- `InteractiveMap` - React-Leaflet map with instant GPX visualization and live POI updates
- `PresetSelectionModal` - Category-organized preset selection (Camping, Accommodation, Food, etc.)
- `FilterSelectionModal` - Custom OSM filter builder (key=value format)
- `Modal` - Reusable modal base component with backdrop and animations

**Custom Hooks:**
- `useWebSocket` - Real-time progress updates via Socket.IO (with polling fallback)

**State Flow:**
```
User uploads GPX → instant client-side parsing → track renders on map
Click Generate → /api/process → job_id
WebSocket/polling updates → progress bar + live POI markers
Completed → interactive map with all results + download buttons
```

**Key Features:**
- **Instant visualization**: GPX track appears immediately after upload (client-side DOMParser)
- **Continuous experience**: Map visible throughout entire workflow
- **Real-time POIs**: Markers appear on map as backend finds them
- **Mobile-first**: Collapsible settings panel, touch-friendly controls
- **Advanced filters**: Preset deletion preserves individual filters, complex filter management
- **Tile persistence**: User's preferred map layer saved to localStorage

### REST API (Flask + SocketIO)
Located in [backend/api/app.py](../backend/api/app.py) - async job processing with polling:

**Endpoints:**
- `GET /health` - Health check
- `GET /api/config` - Returns defaults + presets for UI initialization
- `POST /api/process` - Upload GPX, start async processing, returns `job_id`
- `GET /api/status/{job_id}` - Poll job state (queued → processing → completed/failed)
- `GET /api/job/{job_id}/geojson` - Fetch track + POIs as GeoJSON for map rendering
- `GET /api/download/excel/{filename}` - Download Excel file
- `GET /api/download/html/{filename}` - Download Folium map

**Job Registry:**
Thread-safe in-memory dict tracking job state, progress (0-100%), results, errors.
Background threads execute `run_pipeline()` and update job status via callbacks.

**SocketIO (Optional):**
Real-time updates enabled if SocketIO initialization succeeds, graceful fallback to polling otherwise.

### Key Design Decisions
- **WGS84 geodesic**: All distance calculations use `pyproj.Geod` for accuracy (not Euclidean)
- **Batching**: Multiple search circles combined per Overpass call (controlled by `ALONGGPX_BATCH_KM` environment variable)
- **Auto step_km**: Defaults to 60% of `radius_km` if not set
- **Filter precedence**: CLI/API args override environment variable defaults entirely (not additive)
- **Reusable pipeline**: `cli.main.run_pipeline()` callable from CLI or web backend
- **Async processing**: Web API runs pipeline in background threads, returns immediately with job ID
- **GeoJSON export**: POIs + track converted to GeoJSON for modern map rendering
- **Progress callbacks**: Pipeline supports optional progress callback for real-time updates

## Project Structure

```
AlongGPX/
├── cli/                         # Command-line interface
│   ├── main.py                 # CLI entry + run_pipeline() export
│   └── requirements-cli.txt    # CLI-specific deps
├── backend/                     # Backend services
│   ├── api/                    # Flask REST API
│   │   ├── app.py              # Flask + SocketIO, job registry, endpoints
│   │   └── requirements.txt    # Flask + dependencies
│   └── core/                   # Shared pipeline (DRY - used by CLI & web)
│       ├── __init__.py
│       ├── cli.py              # Argument parsing
│       ├── presets.py          # Filter preset loading/validation
│       ├── gpx_processing.py   # GPX parsing & geodesic metrics
│       ├── overpass.py         # Batched Overpass API queries
│       ├── filtering.py        # Result filtering & distance calc
│       ├── export.py           # Excel export
│       └── folium_map.py       # Folium map generation
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── DevApp.tsx          # Main application
│   │   ├── DevApp.css          # Dark theme styles
│   │   ├── api.ts              # Typed API client
│   │   ├── main.tsx            # React Router entry point
│   │   ├── index.css           # Design system
│   │   ├── components/         # UI components
│   │   │   ├── BrandingHeader.tsx
│   │   │   ├── SettingsSheet.tsx
│   │   │   ├── InteractiveMap.tsx  # React-Leaflet map
│   │   │   ├── PresetSelectionModal.tsx
│   │   │   ├── FilterSelectionModal.tsx
│   │   │   └── Modal.tsx         # Base modal component
│   │   └── hooks/              # Custom React hooks
│   │       └── useWebSocket.ts
│   ├── Dockerfile              # Frontend production build
│   ├── vite.config.ts          # Vite build config
│   └── package.json            # React, axios, leaflet, socket.io-client
├── config/                      # Configuration by usage mode
│   ├── cli/                    # CLI standalone configuration
│   │   ├── .env                # Environment variables for CLI
│   │   ├── .env.example        # Example configuration
│   │   └── README.md           # CLI setup instructions
│   ├── local-dev/              # Local development configuration
│   │   ├── .env                # Shared by Flask + Vite dev server
│   │   ├── .env.example        # Example configuration
│   │   └── README.md           # Local dev setup instructions
│   ├── docker-prod/            # Docker production configuration
│   │   ├── .env                # User-facing Docker settings
│   │   ├── .env.example        # Example configuration
│   │   ├── docker-compose.yml  # Production deployment
│   │   └── README.md           # Docker prod setup instructions
│   └── docker-dev/             # Docker development configuration
│       ├── .env                # Docker dev settings
│       ├── .env.example        # Example configuration
│       ├── docker-compose.yml  # Development with hot reload
│       └── README.md           # Docker dev setup instructions
├── deployment/                  # Shared build artifacts
│   ├── Dockerfile.backend      # Flask backend container
│   ├── Dockerfile.frontend-prod # Nginx + built frontend
│   ├── Dockerfile.frontend-dev # Vite dev server container
│   ├── nginx.conf              # Nginx reverse proxy config
│   └── README.md               # Dockerfile documentation
├── data/                        # Configuration and files
│   ├── presets.yaml            # Filter presets (camp_basic, drinking_water, etc.)
│   ├── input/                  # GPX files (mounted in Docker)
│   └── output/                 # Generated Excel/HTML (timestamped)
├── docs/                        # Documentation
│   ├── quickstart-dev.md       # Development setup & workflows
│   ├── quickstart-cli.md       # CLI setup
│   ├── quickstart-docker.md    # Docker setup
│   ├── FRONTEND.md             # Frontend architecture deep-dive
│   └── IMPLEMENTATION_NOTES.md # Project evolution notes
├── FRONTEND_QUICKREF.md         # Quick reference for developers
└── README.md                    # Project overview
```

## Critical Conventions

### Filter System (`key=value`)
- **Include filters**: OSM tags to search for (e.g., `tourism=camp_site`)
- **Exclude filters**: Remove matches (e.g., `tents=no`)
- Validated in [presets.py](../backend/core/presets.py):`validate_filter_syntax()`
- Matching logic: First matching include filter becomes `Matching Filter` column ([filtering.py](../backend/core/filtering.py))
- **Filter colors**: Web UI assigns colors by filter rank (1st=red, 2nd=orange, 3rd=purple, etc.)

### Coordinate Format
- **Internal (Python)**: Always `(lon, lat)` tuples
- **Folium/display**: Reversed to `[lat, lon]` (see [folium_map.py](../backend/core/folium_map.py))
- **GeoJSON**: Standard format `[lon, lat]` (used by React-Leaflet)

### Distance Calculations
Never use Euclidean distance or projected coordinates for final measurements:
```python
# CORRECT (used in filtering.py)
geod = Geod(ellps="WGS84")
_, _, distance_m = geod.inv(lon1, lat1, lon2, lat2)

# WRONG (only for visualization/interpolation)
track_line = LineString(track_points_m)  # EPSG:3857
```

### Frontend TypeScript Conventions
- **Typed API client**: All responses typed in [api.ts](../frontend/src/api.ts)
- **CSS Modules pattern**: Each component has corresponding `.css` file (e.g., `BrandingHeader.tsx` + `BrandingHeader.css`)
- **Dark theme**: DevApp uses dark color scheme with glassmorphic effects
- **No heavy UI libraries**: Custom CSS with design system (CSS variables in index.css)
- **Error boundaries**: Top-level error handling in DevApp.tsx
- **Real-time updates**: useWebSocket hook for Socket.IO, graceful fallback to 1s polling
- **Client-side GPX parsing**: Browser DOMParser reads GPX immediately for instant visualization
- **LocalStorage persistence**: Tile layer preference saved across sessions

## Configuration System

### Configuration by Usage Mode

Each usage mode has its own isolated configuration directory in `config/`:

- **config/cli/** - CLI standalone (Python script only)
- **config/local-dev/** - Local development (Flask + Vite dev server)
- **config/docker-prod/** - Docker production (Nginx + Flask)
- **config/docker-dev/** - Docker development (hot reload)

### Configuration Loading

**CLI (cli/main.py):**
```python
load_dotenv('config/cli/.env')  # Loads ONLY config/cli/.env
config = load_cli_config(args)  # Builds dict + applies CLI args
```

**Local Dev Flask (backend/api/app.py):**
```python
load_dotenv('config/local-dev/.env')  # Loads ONLY config/local-dev/.env
APP_CONFIG = load_config_from_env()  # Pure env vars
```

**Local Dev Vite (frontend/vite.config.ts):**
```typescript
// Loads: config/local-dev/.env → frontend/.env.local → process.env
const localDevEnv = dotenv.config({ path: '../config/local-dev/.env' })
const personalEnv = dotenv.config({ path: '.env.local' })
const env = { ...localDevEnv, ...personalEnv, ...process.env }
```

**Docker (config/docker-{prod,dev}/docker-compose.yml):**
```yaml
env_file:
  - .env  # Loads config/docker-prod/.env or config/docker-dev/.env
```

### Configuration Hierarchy (Highest → Lowest)

1. **Runtime arguments** (CLI flags or API form parameters)
2. **Environment variables from mode-specific .env** (e.g., `config/cli/.env`)
3. **Built-in defaults** (hardcoded in app.py or cli/main.py)

**Important**: 
- No config sharing between modes - each has complete configuration
- When ANY CLI/API filter args provided (`preset`, `include`, `exclude`), environment variable defaults are completely ignored (not merged) - see [presets.py](../backend/core/presets.py)
- Personal overrides: `frontend/.env.local` (git-ignored) overrides `config/local-dev/.env`

## Development Workflows

### Local Development (Full Stack)
```bash
# Terminal 1: Backend (Flask)
cd /home/rik/AlongGPX
python3 backend/api/app.py
# Runs on http://localhost:5000

# Terminal 2: Frontend (Vite dev server)
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000 with HMR

# Browser: http://localhost:3000
```

### CLI Only (No Web)
```bash
# From repo root with defaults
python3 cli/main.py

# With custom GPX and filters
python3 cli/main.py \
  --gpx-file ./data/input/myroute.gpx \
  --radius-km 10 \
  --preset camp_basic \
  --include "amenity=drinking_water"

# With environment overrides
export ALONGGPX_RADIUS_KM=8
python3 cli/main.py
```

### Docker Production Mode
```bash
cd deployment
docker-compose up -d           # Nginx + Flask backend
curl http://localhost:3000     # Frontend served by Nginx
curl http://localhost:3000/api/health  # API via reverse proxy
```

### Docker Development Mode
```bash
cd deployment
docker-compose -f docker-compose.dev.yml up
# Frontend with hot reload on http://localhost:3000
```

### Frontend Development (Standalone)
```bash
cd frontend
npm run dev          # Dev server with HMR
npm run build        # Production build to dist/
npm run preview      # Preview production build
```

### Testing Changes
- **No automated tests** currently exist
- **Manual validation**: 
  - CLI: Run with `./data/input/track.gpx` → verify Excel columns + map markers
  - Web: Upload GPX → verify progress updates → check downloads
- **Logs**: 
  - Backend: `python3 backend/api/app.py` shows Flask logs
  - Frontend: Browser console shows API calls
  - Docker: `docker-compose logs -f` from deployment/ directory
- **Check batching**: Look for log `Querying X.Xkm track with Y batched Overpass calls`

### Adding New Presets
Edit [data/presets.yaml](../data/presets.yaml):
```yaml
my_preset:
  name: "My Custom Preset"
  category: "Accommodation"
  info: "Description shown in UI"
  include:
    - "amenity=restaurant"
    - "amenity=bar"
  exclude:
    - "diet:vegan=only"
```

**Usage:**
- CLI: `python3 cli/main.py --preset my_preset`
- Web UI: Select from preset dropdown
- API: `curl -F "preset=my_preset" ...`

### Adding New API Endpoints
1. Add route in [backend/api/app.py](../backend/api/app.py)
2. Update TypeScript types in [frontend/src/api.ts](../frontend/src/api.ts)
3. Add client method to `apiClient` object
4. Use in components via `apiClient.newMethod()`

### Adding New UI Components
1. Create `Component.tsx` and `Component.css` in [frontend/src/components/](../frontend/src/components/)
2. Import in [App.tsx](../frontend/src/App.tsx) or other parent
3. Follow naming convention: PascalCase for component, camelCase for props
4. Use CSS variables from [index.css](../frontend/src/index.css) design system

## Common Gotchas

1. **Filter order matters**: Marker colors assigned by include filter rank (1st=red, 2nd=orange, etc.)
2. **Overpass timeouts**: Increase `ALONGGPX_BATCH_KM` environment variable to reduce queries, or decrease for dense areas
3. **Empty results**: Check filter syntax (`key=value`), verify OSM data exists via [overpass-turbo.eu](https://overpass-turbo.eu/)
4. **Duplicate POIs**: Deduplication by OSM ID in [overpass.py](../backend/core/overpass.py)
5. **CLI from wrong directory**: Always run `python3 cli/main.py` from repo root
6. **Docker volume mounts**: Container expects `/app/data/input` and `/app/data/output`
7. **CORS errors in dev**: Vite proxy configured in [vite.config.ts](../frontend/vite.config.ts) - API calls to `/api/*` proxied to Flask
8. **SocketIO fallback**: If WebSocket fails, app automatically falls back to polling
9. **Frontend env vars**: Must start with `VITE_` to be accessible in browser code
10. **Config location**: CLI/backend expect config in `data/` directory (not root)

## External Dependencies

### Backend
- **Flask 3.0** - Web framework
- **Flask-SocketIO** - Real-time updates (optional)
- **gpxpy** - GPX parsing
- **Folium** - Interactive maps
- **pandas** - Data manipulation
- **openpyxl** - Excel export
- **pyproj** - Geodesic calculations
- **Shapely** - Geometric operations
- **requests** - HTTP client

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite 4** - Build tool
- **axios** - HTTP client
- **Leaflet** - Map library
- **react-leaflet** - React bindings for Leaflet
- **socket.io-client** - Real-time updates
- **lucide-react** - Icon library

### External Services
- **Overpass API**: Multiple servers configured via `ALONGGPX_OVERPASS_SERVERS` environment variable, auto-retries with exponential backoff
- **OSM tag reference**: [wiki.openstreetmap.org/wiki/Map_features](https://wiki.openstreetmap.org/wiki/Map_features)

## Environment Variables

### Shared (data/.env)
```
ALONGGPX_PROJECT_NAME=MyProject
ALONGGPX_OUTPUT_PATH=../data/output/
ALONGGPX_RADIUS_KM=5
ALONGGPX_STEP_KM=3
ALONGGPX_BATCH_KM=50
ALONGGPX_TIMEZONE=Europe/Berlin
ALONGGPX_HOSTNAME=localhost  # For Vite HMR in Docker
```

### Backend (backend/api/.env)
```
FLASK_ENV=development
FLASK_PORT=5000
```

### Frontend (frontend/.env.local)
```
VITE_API_BASE_URL=http://localhost:5000
VITE_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Docker (deployment/.env)
```
FLASK_ENV=production
FLASK_PORT=5000
```

## File Organization by Role

### Backend Developer
- **[backend/api/app.py](../backend/api/app.py)** - Add API endpoints here
- **[backend/core/](../backend/core/)** - Modify pipeline logic (GPX, Overpass, filtering)
- **[deployment/.env](../deployment/.env)** or **[deployment/docker-compose.yml](../deployment/docker-compose.yml)** - Adjust defaults

### Frontend Developer
- **[frontend/src/DevApp.tsx](../frontend/src/DevApp.tsx)** - Main orchestration
- **[frontend/src/components/](../frontend/src/components/)** - UI components
- **[frontend/src/api.ts](../frontend/src/api.ts)** - API client
- **[frontend/src/hooks/useWebSocket.ts](../frontend/src/hooks/useWebSocket.ts)** - Real-time hook
- **[frontend/src/index.css](../frontend/src/index.css)** - Design system

### DevOps
- **[deployment/docker-compose.yml](../deployment/docker-compose.yml)** - Production deployment
- **[deployment/nginx.conf](../deployment/nginx.conf)** - Reverse proxy
- **[deployment/Dockerfile](../deployment/Dockerfile)** - Backend image
- **[deployment/Dockerfile.nginx](../deployment/Dockerfile.nginx)** - Frontend image

### Data/Config
- **[data/presets.yaml](../data/presets.yaml)** - Filter presets
- **[deployment/.env](../deployment/.env)** - Environment configuration
- **[data/input/](../data/input/)** - GPX files
- **[data/output/](../data/output/)** - Results (Excel, HTML, timestamped)

## API Integration Examples

### Python (calling run_pipeline directly)
```python
import sys, os
sys.path.insert(0, '/home/rik/AlongGPX')
from cli.main import run_pipeline

# Configuration is loaded from environment variables
# Set environment variables before running:
# export ALONGGPX_RADIUS_KM=10
# export ALONGGPX_GPX_FILE=data/input/track.gpx

result = run_pipeline(
    cli_presets=['camp_basic'], 
    cli_include=['amenity=drinking_water'],
    cli_exclude=None
)
# Returns: {excel_path, html_path, dataframe, rows_count, track_length_km}
```

### cURL (REST API)
```bash
# Upload and process
curl -X POST http://localhost:5000/api/process \
  -F "file=@track.gpx" \
  -F "project_name=MyTrip" \
  -F "radius_km=10" \
  -F "preset=camp_basic" \
  -F "include=amenity=drinking_water"
# Returns: {"job_id": "abc-123", "status_url": "/api/status/abc-123"}

# Poll status
curl http://localhost:5000/api/status/abc-123
# Returns: {"state": "processing", "percent": 45, "message": "Overpass queries 3/7", ...}

# Download Excel
curl -O http://localhost:5000/api/download/excel/MyTrip_20260129_120000.xlsx
```

### TypeScript (Frontend)
```typescript
import { apiClient } from './api'

// Start processing
const response = await apiClient.startProcessing(
  gpxFile,
  'MyTrip',
  10,
  ['amenity=drinking_water'],
  [],
  ['camp_basic']
)

// Poll status
const status = await apiClient.getJobStatus(response.job_id)

// Get GeoJSON for map
const geojson = await apiClient.getGeoJson(response.job_id)
```

## Deployment Scenarios

### Single-User Local
```bash
# Just run backend + frontend locally
python3 backend/api/app.py &
cd frontend && npm run dev
```

### Multi-User Production (Local Build)
```bash
# Docker with local source builds
cd deployment
docker compose up --build -d
# Access at http://server:3000
```

## Release & Git Workflow
- Branch for features: `git checkout -b feature/description`
- Commit with scope: 
  - `git commit -m "feat(frontend): add new component"`
  - `git commit -m "fix(backend): correct job registry locking"`
  - `git commit -m "docs: update API examples"`
- Push to GitHub: `git push -u origin feature/description`
- Open PR and request review before merging to main
- Use semantic versioning for releases

## Performance Considerations
- **Overpass batching**: Adjust `batch_km` based on track length and POI density
- **Frontend polling**: 1s interval balances responsiveness vs server load
- **GeoJSON size**: Large tracks/POIs may cause browser memory issues (consider pagination)
- **Docker resources**: Backend threads consume memory during processing
- **File storage**: Output directory grows with each run (implement cleanup cron)
