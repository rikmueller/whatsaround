# AlongGPX CLI Configuration

This directory contains configuration for **CLI standalone usage** of AlongGPX.

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cp config/cli/.env.example config/cli/.env
   ```

2. **Edit `config/cli/.env`** with your preferences:
   - Set `ALONGGPX_PROJECT_NAME` for output file naming
   - Adjust `ALONGGPX_RADIUS_KM` for search radius
   - Configure filters or presets

3. **Run the CLI:**
   ```bash
   python3 cli/main.py --gpx-file data/input/myroute.gpx --preset camp_sites_tent
   ```

## Configuration Hierarchy

CLI arguments override environment variables:

```
CLI Arguments (highest priority)
    ↓
config/cli/.env
    ↓
Hardcoded defaults (lowest priority)
```

## Common Use Cases

### Search for Campsites
```bash
python3 cli/main.py --preset camp_sites_tent --radius-km 10
```

### Custom Filters
```bash
python3 cli/main.py \
  --include "amenity=drinking_water" \
  --include "tourism=camp_site" \
  --exclude "tents=no"
```

### Process Specific GPX
```bash
python3 cli/main.py --gpx-file ./data/input/bikepacking-route.gpx
```

## Output

Results are saved to `data/output/`:
- `{PROJECT_NAME}.xlsx` - Excel spreadsheet with POI data
- `{PROJECT_NAME}.html` - Interactive Folium map

## See Also

- [Main README](../../README.md) - Project overview
- [data/presets.yaml](../../data/presets.yaml) - Available presets
- [docs/quickstart-cli.md](../../docs/quickstart-cli.md) - Detailed CLI guide
