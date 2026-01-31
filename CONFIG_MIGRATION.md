# Configuration Migration Guide

The project configuration has been restructured. If you have existing `.env` files, follow this guide to migrate.

## What Changed?

Configuration is now organized by **usage mode** with isolated directories:

```
OLD structure:              NEW structure:
cli/.env                 →  config/cli/.env
deployment/.env          →  config/docker-prod/.env (or config/docker-dev/.env)
frontend/.env.local      →  frontend/.env.local (unchanged)
```

## Migration Steps

### For CLI Users

```bash
# If you have cli/.env, move it:
mv cli/.env config/cli/.env

# Or copy the example and reconfigure:
cp config/cli/.env.example config/cli/.env
# Then edit config/cli/.env with your settings
```

### For Local Development Users

```bash
# Create new local-dev config:
cp config/local-dev/.env.example config/local-dev/.env

# Copy your old settings if you had cli/.env:
# - ALONGGPX_* variables
# - FLASK_* variables

# Personal overrides remain in frontend/.env.local (no change)
```

### For Docker Users

**Production:**
```bash
# If you have deployment/.env, move it:
mv deployment/.env config/docker-prod/.env

# Or copy the example:
cp config/docker-prod/.env.example config/docker-prod/.env
```

**Development:**
```bash
# Copy the example:
cp config/docker-dev/.env.example config/docker-dev/.env
```

**Update your commands:**
```bash
# OLD:
cd deployment && docker compose up -d

# NEW:
cd config/docker-prod && docker compose up -d
# or
cd config/docker-dev && docker compose up
```

## What's Different?

### No More Config Sharing

Each mode has its **own complete .env file**:
- CLI has everything it needs in `config/cli/.env`
- Local dev has everything in `config/local-dev/.env` (shared by Flask + Vite)
- Docker prod has settings in `config/docker-prod/.env`
- Docker dev has settings in `config/docker-dev/.env`

### Simplified Loading

**Before (complex cascade):**
```
cli/.env → frontend/.env → frontend/.env.local → process.env
```

**Now (simple and clear):**
```
config/local-dev/.env → frontend/.env.local → process.env
```

### Independent Defaults

Each mode can have different defaults without affecting others:
- CLI might default to `RADIUS_KM=10`
- Local dev might default to `RADIUS_KM=5`
- Docker might default to `RADIUS_KM=3`

## Backwards Compatibility

Old paths still work temporarily:
- `cli/.env` will be loaded if `config/cli/.env` doesn't exist
- But this is **deprecated** and will be removed in a future version

## Need Help?

- **CLI setup**: See [config/cli/README.md](config/cli/README.md)
- **Local dev setup**: See [config/local-dev/README.md](config/local-dev/README.md)
- **Docker prod**: See [config/docker-prod/README.md](config/docker-prod/README.md)
- **Docker dev**: See [config/docker-dev/README.md](config/docker-dev/README.md)
