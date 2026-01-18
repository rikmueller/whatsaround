# osm_finder

osm_finder is a modular Python tool that analyzes OpenStreetMap POIs along a GPX track.  
It combines GPX processing, Overpass API queries, flexible OSM filters, Excel export, and interactive Folium maps.

## Features
- Read GPX tracks and compute total distance
- Run segmented Overpass queries along the track
- Use flexible OSM include and exclude filters
- Use preset filter profiles for common search types
- Validate filters automatically
- Export all results to Excel
- Generate an interactive Folium map with track and markers
- Fully configurable through YAML and command line arguments

## Installation
### Clone the repository
```bash
git clone https://github.com/your_username/osm_finder.git
cd osm_finder
```

### Create a virtual environment
It's recommended to use a Python virtual environment to avoid conflicts with system packages.

**On Linux/macOS:**
```bash
python3 -m venv venv_osm_finder
source venv_osm_finder/bin/activate
```

**On Windows:**
```bash
python -m venv venv_osm_finder
venv_osm_finder\Scripts\activate
```

Your prompt should now show `(venv_osm_finder)` at the beginning, indicating the virtual environment is active.

### Install dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install gpxpy shapely pyproj requests tqdm folium pyyaml pandas
```

## Configuration

All default settings are stored in `config.yaml`.

### Example config:

```yaml
project:
  # Name used for output files (xlsx and html)
  name: "MyProject"
  # Directory where output files will be saved
  output_path: "./output/"

input:
  # Path to the GPX file containing the track to analyze
  gpx_file: "./input/track.gpx"

search:
  # Search radius in kilometers around each track segment
  radius_km: 5
  # Distance between Overpass query points along the track (in km)
  # Set to null to auto-calculate as 60% of radius_km (highly suggested)
  step_km: null
  # OSM tags to search for (include filters)
  include:
    - "tourism=camp_site"
  # OSM tags to exclude from results (exclude filters)
  exclude:
    - "tents=no"
    - "camp_site:tent=no"

map:
  # Initial zoom level for the Folium map (1-18)
  zoom_start: 10
  # Color of the track line on the map
  track_color: "blue"
  # Marker colors based on distance to track
  marker_colors:
    # Color for objects within 2 km of track
    near: "green"
    # Color for objects 2-5 km from track
    mid: "orange"
    # Color for objects more than 5 km from track
    far: "red"

overpass:
  # Number of retry attempts for failed Overpass API requests
  retries: 5
  # List of Overpass API endpoints (multiple servers for redundancy)
  servers:
    - "https://overpass-api.de/api/interpreter"
    - "https://overpass.private.coffee/api/interpreter"
    - "https://lz4.overpass-api.de/api/interpreter"

# Path to the presets file containing predefined filter profiles (don´t change)
presets_file: "presets.yaml"
```

## Presets

The file `presets.yaml` contains predefined filter profiles.

### Example presets:

```yaml
presets:
  camp_basic:
    include:
      - tourism=camp_site
    exclude:
      - tents=no
      - camp_site:tent=no

  camp_and_caravan:
    include:
      - tourism=camp_site
      - tourism=caravan_site

  shelters:
    include:
      - amenity=shelter

  drinking_water:
    include:
      - amenity=drinking_water
```

## Usage

Run with default configuration:
```bash
python3 main.py
```

Override GPX file:
```bash
python3 main.py --gpx-file mytrack.gpx
```

Use a preset:
```bash
python3 main.py --preset camp_and_caravan
```

Combine presets:
```bash
python3 main.py --preset camp_basic --preset drinking_water
```

Add include filters:
```bash
python3 main.py --include amenity=toilets
```

Add exclude filters:
```bash
python3 main.py --exclude fee=yes
```

Full example:
```bash
python3 main.py --preset camp_basic --include amenity=toilets --exclude fee=yes --gpx-file mytrack.gpx --project-name Tour2025
```

## Output

The tool generates two files:

- `<project_name>.xlsx`
- `<project_name>.html`

Both files are saved in the directory defined by `project.output_path`.

## Technical Notes

- Overpass queries are executed in segments along the track
- Distances are computed using WGS84 geodesic calculations
- Track projection uses EPSG 3857
- Marker colors depend on distance to the track
- Filters are validated to ensure `key=value` format
- Duplicate results are removed

## Contributing

Pull requests are welcome. Please open an issue if you find bugs or want to request features.


