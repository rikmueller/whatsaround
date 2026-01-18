import os
import yaml


def load_yaml_config(path: str) -> dict:
    """
    Load a YAML configuration file.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def merge_cli_into_config(cfg: dict, args) -> dict:
    """
    Merge CLI arguments into YAML configuration.
    Only set CLI values override YAML.
    """
    if args.project_name:
        cfg["project"]["name"] = args.project_name
    if args.output_path:
        cfg["project"]["output_path"] = args.output_path
    if args.gpx_file:
        cfg["input"]["gpx_file"] = args.gpx_file
    if args.radius_km is not None:
        cfg["search"]["radius_km"] = args.radius_km
    if args.step_km is not None:
        cfg["search"]["step_km"] = args.step_km

    # STEP_KM: if None → 60% of radius_km
    if cfg["search"]["step_km"] is None:
        cfg["search"]["step_km"] = cfg["search"]["radius_km"] * 0.6

    # Normalize output path
    cfg["project"]["output_path"] = os.path.abspath(cfg["project"]["output_path"])

    return cfg


def load_and_merge_config(config_path: str, args) -> dict:
    """
    Load YAML configuration and merge CLI overrides into it.
    """
    cfg = load_yaml_config(config_path)
    cfg = merge_cli_into_config(cfg, args)
    return cfg
