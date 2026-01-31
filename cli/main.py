#!/usr/bin/env python3
import sys
import os
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.cli import parse_cli_args
from backend.core.presets import load_presets, apply_presets_to_filters
from backend.core.gpx_processing import load_gpx_track, compute_track_metrics
from backend.core.overpass import query_overpass_segmented
from backend.core.filtering import filter_elements_and_build_rows
from backend.core.export import export_to_excel
from backend.core.folium_map import build_folium_map

logger = logging.getLogger(__name__)


def load_cli_config(args) -> dict:
    """
    Load CLI configuration from config/cli/.env file and apply CLI argument overrides.
    
    Args:
        args: Parsed CLI arguments from argparse
    
    Returns:
        dict: Complete configuration dictionary
    """
    # Load config/cli/.env file
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(repo_root, 'config', 'cli', '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded configuration from {env_path}")
    else:
        logger.warning(f"No .env file found at {env_path}, using defaults")
    
    # Helper functions for parsing
    def parse_semicolon_list(value: str | None) -> list:
        if not value:
            return []
        return [item.strip() for item in value.split(';') if item.strip()]
    
    def get_float(key: str, default: float | None = None) -> float | None:
        value = os.getenv(key)
        if value is None or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_int(key: str, default: int) -> int:
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    # Build config from environment variables
    config = {
        'project': {
            'name': os.getenv('ALONGGPX_PROJECT_NAME', 'AlongGPX'),
            'output_path': os.getenv('ALONGGPX_OUTPUT_PATH', '../data/output'),
            'timezone': os.getenv('ALONGGPX_TIMEZONE', 'UTC'),
        },
        'input': {
            'gpx_file': os.getenv('ALONGGPX_GPX_FILE', '../data/input/example.gpx'),
        },
        'search': {
            'radius_km': get_float('ALONGGPX_RADIUS_KM', 5.0),
            'step_km': get_float('ALONGGPX_STEP_KM'),  # None = auto-calculate
            'presets': parse_semicolon_list(os.getenv('ALONGGPX_PRESETS')),
            'include': parse_semicolon_list(os.getenv('ALONGGPX_SEARCH_INCLUDE')),
            'exclude': parse_semicolon_list(os.getenv('ALONGGPX_SEARCH_EXCLUDE')),
        },
        'overpass': {
            'retries': get_int('ALONGGPX_OVERPASS_RETRIES', 5),
            'batch_km': get_float('ALONGGPX_BATCH_KM', 50.0),
            'servers': parse_semicolon_list(
                os.getenv('ALONGGPX_OVERPASS_SERVERS')
            ) or [
                'https://overpass.private.coffee/api/interpreter',
                'https://overpass-api.de/api/interpreter',
                'https://lz4.overpass-api.de/api/interpreter',
            ],
        },
        'map': {
            'track_color': os.getenv('ALONGGPX_TRACK_COLOR', 'blue'),
            'default_marker_color': os.getenv('ALONGGPX_DEFAULT_MARKER_COLOR', 'gray'),
            'marker_color_palette': parse_semicolon_list(
                os.getenv('ALONGGPX_MARKER_COLOR_PALETTE')
            ) or ['orange', 'purple', 'green', 'blue', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'pink'],
        },
        'presets_file': os.getenv('ALONGGPX_PRESETS_FILE', 'data/presets.yaml'),
    }
    
    # Apply CLI argument overrides (highest precedence)
    if args.project_name:
        config['project']['name'] = args.project_name
    if args.output_path:
        config['project']['output_path'] = args.output_path
    if args.gpx_file:
        config['input']['gpx_file'] = args.gpx_file
    if args.radius_km is not None:
        config['search']['radius_km'] = args.radius_km
    if args.step_km is not None:
        config['search']['step_km'] = args.step_km
    
    # Auto-calculate step_km if not set
    if config['search']['step_km'] is None:
        config['search']['step_km'] = config['search']['radius_km'] * 0.6
    
    # Resolve relative paths to absolute (relative to repo root, already calculated above)
    config['project']['output_path'] = os.path.abspath(
        os.path.join(repo_root, config['project']['output_path'])
    )
    config['input']['gpx_file'] = os.path.abspath(
        os.path.join(repo_root, config['input']['gpx_file'])
    )
    config['presets_file'] = os.path.abspath(
        os.path.join(repo_root, config['presets_file'])
    )
    
    return config


def run_pipeline(
    config: dict,
    cli_presets: list | None = None,
    cli_include: list | None = None,
    cli_exclude: list | None = None,
    progress_callback=None,
    excel_filename: str | None = None,
    html_filename: str | None = None,
):
    """
    Core pipeline function that can be called from CLI or web app.
    
    Args:
        config: Dictionary containing all configuration (project, search, overpass, map, etc.)
        cli_presets: List of preset names to apply
        cli_include: List of include filters
        cli_exclude: List of exclude filters
        progress_callback: Callable(percent, message) for progress updates
        excel_filename: Optional filename for Excel output (UUID-based). If None, uses project_name.xlsx
        html_filename: Optional filename for HTML output (UUID-based). If None, uses project_name.html
    
    Returns:
        dict: Results containing paths to Excel and HTML files, dataframe, and metadata
    """
    def report_progress(percent: float, message: str):
        if progress_callback:
            try:
                progress_callback(percent, message)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)

    report_progress(5, "Preparing pipeline...")
    
    # Load presets (path should already be absolute from load_cli_config)
    presets_file = config.get("presets_file", "data/presets.yaml")
    if not os.path.isabs(presets_file):
        # If called from backend, make relative paths absolute from repo root
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        presets_file = os.path.abspath(os.path.join(repo_root, presets_file))
    
    presets = load_presets(presets_file)

    # Apply presets to include/exclude
    include_filters, exclude_filters = apply_presets_to_filters(
        presets,
        config["search"]["include"],
        config["search"]["exclude"],
        cli_presets,
        cli_include,
        cli_exclude,
    )

    # Load GPX and prepare track
    report_progress(10, "Loading GPX track...")
    track_points = load_gpx_track(config["input"]["gpx_file"])
    track_info = compute_track_metrics(track_points)
    report_progress(
        20,
        f"Track loaded: {len(track_points)} points, {track_info['total_length_km']:.1f} km",
    )

    # Overpass queries along the track
    def overpass_progress(done: int, total: int):
        base = 25
        span = 45
        fraction = done / total if total else 1
        percent = base + fraction * span
        report_progress(percent, f"Overpass queries {done}/{total}")

    elements = query_overpass_segmented(
        track_points=track_points,
        track_info=track_info,
        radius_km=config["search"]["radius_km"],
        step_km=config["search"]["step_km"],
        overpass_cfg=config["overpass"],
        include_filters=include_filters,
        progress_cb=overpass_progress,
    )
    report_progress(75, f"Fetched {len(elements)} raw results. Filtering...")

    # Filter elements and generate tabular data
    rows, df = filter_elements_and_build_rows(
        elements=elements,
        track_points=track_points,
        track_info=track_info,
        radius_km=config["search"]["radius_km"],
        exclude_filters=exclude_filters,
        include_filters=include_filters,
    )
    report_progress(82, f"Filtered {len(rows)} results. Exporting...")

    # Export to Excel
    excel_path = export_to_excel(
        df=df,
        output_path=config["project"]["output_path"],
        project_name=config["project"]["name"],
        filename=excel_filename,
    )
    report_progress(90, "Excel exported. Building map...")

    # Generate Folium map
    html_path = build_folium_map(
        df=df,
        track_points=track_points,
        output_path=config["project"]["output_path"],
        project_name=config["project"]["name"],
        map_cfg=config["map"],
        include_filters=include_filters,
        filename=html_filename,
    )
    report_progress(95, "Map generated. Finalizing...")

    return {
        "excel_path": excel_path,
        "html_path": html_path,
        "dataframe": df,
        "rows_count": len(df),
        "track_length_km": track_info["total_length_km"],
    }


def main():
    """CLI entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Read CLI arguments
    args = parse_cli_args()

    # Load configuration from cli/.env and apply CLI overrides
    config = load_cli_config(args)

    # Use CLI presets if provided, otherwise fall back to config presets
    presets = args.presets if args.presets is not None else config['search'].get('presets', [])
    
    try:
        result = run_pipeline(
            config,
            cli_presets=presets,
            cli_include=args.include,
            cli_exclude=args.exclude,
        )
        print(f"✅ Done! {result['rows_count']} objects found.")
        print(f"📄 Excel: {result['excel_path']}")
        print(f"🌍 Map: {result['html_path']}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Aborted by user.")
        sys.exit(1)
