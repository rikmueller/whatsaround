import argparse


def parse_cli_args():
    """
    Define and parse CLI arguments.
    All settings loaded from cli/.env can be overridden by these arguments.
    """
    parser = argparse.ArgumentParser(
        description="Find OSM objects along a GPX track (Overpass, Excel, Folium)."
    )

    parser.add_argument(
        "--project-name",
        type=str,
        help="Project name (overrides ALONGGPX_PROJECT_NAME from cli/.env)",
    )

    parser.add_argument(
        "--output-path",
        type=str,
        help="Output path (overrides ALONGGPX_OUTPUT_PATH from cli/.env)",
    )

    parser.add_argument(
        "--gpx-file",
        type=str,
        help="GPX file path (overrides ALONGGPX_GPX_FILE from cli/.env)",
    )

    parser.add_argument(
        "--radius-km",
        type=float,
        help="Search radius in km (overrides ALONGGPX_RADIUS_KM)",
    )

    parser.add_argument(
        "--step-km",
        type=float,
        help="Distance between query points in km (overrides ALONGGPX_STEP_KM)",
    )

    parser.add_argument(
        "--include",
        action="append",
        default=None,
        help="Include filter (key=value). Can be used multiple times.",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Exclude filter (key=value). Can be used multiple times.",
    )

    parser.add_argument(
        "--preset",
        dest="presets",
        action="append",
        default=None,
        help="Preset name from presets.yaml. Can be used multiple times.",
    )

    return parser.parse_args()
