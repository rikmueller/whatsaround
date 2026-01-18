import time
import requests
import math


def build_overpass_query(lon, lat, radius_km, include_filters):
    """
    Build an Overpass query with dynamic include filters.
    """
    include_parts = []
    for inc in include_filters:
        key, value = inc.split("=", 1)
        for obj_type in ("node", "way", "relation"):
            include_parts.append(
                f'{obj_type}["{key}"="{value}"](around:{radius_km * 1000},{lat},{lon});'
            )

    include_block = "\n      ".join(include_parts)

    query = f"""
    [out:json][timeout:60];
    (
      {include_block}
    );
    out center tags;
    """
    return query


def query_overpass_with_retries(query: str, overpass_cfg: dict):
    """
    Execute an Overpass query with multiple servers and retries.
    """
    servers = overpass_cfg.get("servers", [])
    retries = overpass_cfg.get("retries", 3)

    for attempt in range(retries):
        for server in servers:
            try:
                r = requests.post(server, data=query, timeout=60)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        wait = 2 * (attempt + 1)
        print(f"⚠️ Overpass error – Retrying in {wait}s")
        time.sleep(wait)

    print("❌ Overpass permanently failed.")
    return {"elements": []}


def query_overpass_segmented(
    track_points,
    track_info,
    radius_km: float,
    step_km: float,
    overpass_cfg: dict,
    include_filters: list,
):
    """
    Execute segmented Overpass queries along the track.
    """
    from shapely.geometry import LineString
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    track_points_m = [transformer.transform(*p) for p in track_points]
    track_line = LineString(track_points_m)

    total_track_length_km = track_info["total_length_km"]
    track_length_m_proj = track_line.length

    def point_at_km(km):
        m = (km / total_track_length_km) * track_length_m_proj
        x, y = track_line.interpolate(m).xy
        lon, lat = transformer.transform(x[0], y[0], direction="INVERSE")
        return lon, lat

    num_steps = math.ceil(total_track_length_km / step_km)
    print(f"🔍 Starting {num_steps} segmented Overpass queries...")

    from tqdm import tqdm

    all_elements = []
    seen_ids = set()

    for step in tqdm(range(num_steps + 1), desc="⏳ Overpass queries running"):
        km = step * step_km
        lon, lat = point_at_km(km)

        query = build_overpass_query(lon, lat, radius_km, include_filters)
        data = query_overpass_with_retries(query, overpass_cfg)

        for el in data.get("elements", []):
            if el["id"] in seen_ids:
                continue
            seen_ids.add(el["id"])
            all_elements.append(el)

    return all_elements
