# AlongGPX Docker Development Configuration

This directory contains configuration for **Docker development mode** with hot reload for both frontend and backend.

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cp config/docker-dev/.env.example config/docker-dev/.env
   ```

2. **Start development containers:**
   ```bash
   cd config/docker-dev
   docker compose up
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000 (Vite dev server with HMR)
   - Backend API: http://localhost:5000

## Architecture

```
frontend:3000 (Vite dev server with hot reload)
    ↓ proxy /api/* to
backend:5000 (Flask with auto-reload)
```

## Services

### backend (port 5000)
- Flask API with `FLASK_ENV=development`
- Auto-reloads on Python file changes
- Source code mounted from host: `../../backend`, `../../cli`

### frontend (port 3000)
- Vite dev server with Hot Module Replacement
- Auto-reloads on TypeScript/React changes
- Source code mounted from host: `../../frontend/src`

## Hot Reload

**Backend changes:**
- Edit any Python file in `backend/` or `cli/`
- Flask automatically restarts
- Check logs: `docker compose logs -f backend`

**Frontend changes:**
- Edit any file in `frontend/src/`
- Browser updates instantly via HMR
- No container restart needed

## Development Workflow

1. Make changes to source code (backend or frontend)
2. See changes immediately without rebuilding containers
3. Debug via container logs or browser console

## Remote Access (Optional)

To access from another device on your network:

1. **Find your machine's IP:**
   ```bash
   ip addr show | grep inet
   ```

2. **Update `.env`:**
   ```bash
   ALONGGPX_HOSTNAME=192.168.1.100
   ```

3. **Restart containers:**
   ```bash
   docker compose restart
   ```

4. **Access from other device:** http://192.168.1.100:3000

## Differences from Production

| Feature | Development | Production |
|---------|-------------|------------|
| Frontend | Vite dev server | Pre-built static files |
| Backend | Auto-reload | Optimized runtime |
| Code changes | Live reload | Requires rebuild |
| Performance | Slower (dev mode) | Fast (production) |
| Port access | Both 3000 & 5000 | Only 3000 (Nginx) |

## Logs

View real-time logs:
```bash
docker compose logs -f           # All services
docker compose logs -f backend   # Backend only
docker compose logs -f frontend  # Frontend only
```

## Troubleshooting

### HMR not working
Check `ALONGGPX_HOSTNAME` matches your access method:
- Local: `localhost`
- Remote: Your machine's IP address

### Backend changes not reloading
Ensure `FLASK_ENV=development` in docker-compose.yml.

### Permission errors
Volume mounts may have permission issues:
```bash
chmod 777 ../../data/output
```

## See Also

- [../../docs/quickstart-dev.md](../../docs/quickstart-dev.md) - Local development guide
- [../../frontend/README.md](../../frontend/README.md) - Frontend architecture
- [docker-compose.yml](./docker-compose.yml) - Service configuration
