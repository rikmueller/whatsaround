#!/usr/bin/env python3
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cli import parse_cli_args
from core.config import load_and_merge_config
from core.presets import load_presets, apply_presets_to_filters
from core.gpx_processing import load_gpx_track, compute_track_metrics
from core.overpass import query_overpass_segmented
from core.filtering import filter_elements_and_build_rows
from core.export import export_to_excel
from core.folium_map import build_folium_map

logger = logging.getLogger(__name__)


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
    
    # Load presets
    presets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                "config", config.get("presets_file", "presets.yaml"))
    presets = load_presets(presets_path)

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

    # If config path is default (not overridden), resolve it relative to repo root
    if args.config == "config.yaml":
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.config = os.path.join(repo_root, "config", "config.yaml")

    # Merge configuration from YAML + CLI
    config = load_and_merge_config(args.config, args)

    try:
        result = run_pipeline(
            config,
            cli_presets=args.presets,
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
