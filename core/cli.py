import argparse


def parse_cli_args():
    """
    Define and parse CLI arguments.
    YAML config can be overridden/supplemented.
    """
    parser = argparse.ArgumentParser(
        description="Find OSM objects along a GPX track (Overpass, Excel, Folium)."
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to YAML configuration file (Default: config.yaml)",
    )

    parser.add_argument(
        "--project-name",
        type=str,
        help="Project name, overrides project.name from config.yaml",
    )

    parser.add_argument(
        "--output-path",
        type=str,
        help="Output path, overrides project.output_path from config.yaml",
    )

    parser.add_argument(
        "--gpx-file",
        type=str,
        help="GPX file, overrides input.gpx_file from config.yaml",
    )

    parser.add_argument(
        "--radius-km",
        type=float,
        help="Search radius in km, overrides search.radius_km",
    )

    parser.add_argument(
        "--step-km",
        type=float,
        help="Distance of Overpass queries in km, overrides search.step_km",
    )

    parser.add_argument(
        "--include",
        action="append",
        default=None,
        help="Additional include filter (key=value). Can be used multiple times.",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Additional exclude filter (key=value). Can be used multiple times.",
    )

    parser.add_argument(
        "--preset",
        dest="presets",
        action="append",
        default=None,
        help="Name of a preset from presets.yaml. Can be used multiple times.",
    )

    return parser.parse_args()
