Reverse proxy configuration:
- Routes `/api/*` → Flask backend
- Routes `/socket.io/*` → WebSocket/polling
- Serves frontend static files
- Used by: `Dockerfile.frontend-prod`

## 🔧 Building Manually

If you need to build containers manually:

```bash
# Backend
docker build -f deployment/Dockerfile.backend -t alonggpx-backend .

# Frontend (production)
docker build -f deployment/Dockerfile.frontend-prod -t alonggpx-frontend .

# Frontend (development)
docker build -f deployment/Dockerfile.frontend-dev -t alonggpx-frontend-dev .
```

## 📚 See Also

- [config/docker-prod/README.md](../config/docker-prod/README.md) - Production setup guide
- [config/docker-dev/README.md](../config/docker-dev/README.md) - Development setup guide
- [docs/quickstart-docker.md](../docs/quickstart-docker.md) - Detailed Docker documentation
- You need instant feedback on UI changes
- You're debugging frontend issues

---

## Common Configuration

Both compose files share:
- Same port mappings (backend: 5000, frontend: 3000)
- Same volume structure (data/input, data/output)
- Same environment variable handling (.env file)
- Health checks for both services

---

## Questions?

- **"Which compose file should I use?"** → Start with `docker-compose.yml`
- **"How do I customize presets?"** → See [../docs/quickstart-docker.md](../docs/quickstart-docker.md)
- **"Can I switch between them?"** → Yes, just bring down one and start another
- **"Do I need to rebuild images?"** → Yes, use `docker compose up --build -d`
