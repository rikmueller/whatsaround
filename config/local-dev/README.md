# AlongGPX Local Development Configuration

This directory contains configuration for **local development** with both Flask backend and Vite frontend running on your machine.

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cp config/local-dev/.env.example config/local-dev/.env
   ```

2. **Start the backend** (Terminal 1):
   ```bash
   python3 backend/api/app.py
   # Runs on http://localhost:5000
   ```

3. **Start the frontend** (Terminal 2):
   ```bash
   cd frontend
   npm install
   npm run dev
   # Runs on http://localhost:3000 with hot reload
   ```

4. **Open browser:** http://localhost:3000

## Configuration Loading

Both Flask and Vite load from the same `config/local-dev/.env` file:

```
config/local-dev/.env (shared)
    ├─> Flask (backend/api/app.py)
    └─> Vite (frontend/vite.config.ts)
```

### Personal Overrides

Create `frontend/.env.local` (git-ignored) for personal settings:

```bash
# Override backend URL for remote Flask instance
VITE_BACKEND_URL=http://192.168.1.100:5000

# Override HMR host for remote development
ALONGGPX_HOSTNAME=192.168.1.100
```

## How It Works

- **Vite dev server** proxies `/api/*` requests to Flask backend
- **Flask backend** serves API and processes GPX files
- **Hot Module Replacement** auto-refreshes frontend on code changes
- **Backend auto-reload** restarts Flask on Python file changes (FLASK_ENV=development)

## API Endpoints

- `GET /health` - Backend health check
- `GET /api/config` - Get configuration and presets
- `POST /api/process` - Upload GPX and start processing
- `GET /api/status/{job_id}` - Poll job status
- `GET /api/download/excel/{job_id}` - Download Excel results
- `GET /api/download/html/{job_id}` - Download interactive map

## Troubleshooting

### Backend not found (ERR_CONNECTION_REFUSED)
Check that Flask is running on port 5000:
```bash
curl http://localhost:5000/health
```

### CORS errors
Vite proxy should handle this automatically. Check `frontend/vite.config.ts` proxy settings.

### Port already in use
Change ports in `config/local-dev/.env`:
```bash
FLASK_PORT=5001
VITE_BACKEND_URL=http://localhost:5001
```

## See Also

- [docs/quickstart-dev.md](../../docs/quickstart-dev.md) - Detailed development guide
- [frontend/README.md](../../frontend/README.md) - Frontend architecture
- [backend/api/app.py](../../backend/api/app.py) - Backend implementation
