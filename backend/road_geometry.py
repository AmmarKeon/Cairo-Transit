"""
Road geometry via Valhalla API - real OSM road paths.
No persistent cache (serverless), fetches on each request.
"""
import json
import math
import time
import urllib.request
import urllib.error
from typing import List, Optional

VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"

# Simple in-memory cache for this instance (survives across warm invocations)
_geometry_cache: dict = {}

def _decode_polyline6(encoded: str) -> List[List[float]]:
    """Decode a precision-6 encoded polyline to [[lat, lng], ...]."""
    coords = []
    index = 0
    lat = 0
    lng = 0
    while index < len(encoded):
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coords.append([lat / 1e6, lng / 1e6])

    return coords


def _rate_limited_call():
    """Simple rate limiting - 100ms between calls."""
    time.sleep(0.1)


def get_segment_coords(from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[List[List[float]]]:
    """Get road geometry for a single segment. Returns [[lat, lng], ...] or None."""
    cache_key = f"{round(from_lng,6)},{round(from_lat,6)};{round(to_lng,6)},{round(to_lat,6)}"

    if cache_key in _geometry_cache:
        return _geometry_cache[cache_key]

    _rate_limited_call()

    payload = json.dumps({
        "locations": [
            {"lat": from_lat, "lon": from_lng},
            {"lat": to_lat, "lon": to_lng}
        ],
        "costing": "auto",
        "directions_options": {"units": "kilometers"}
    }).encode()

    try:
        req = urllib.request.Request(
            VALHALLA_URL,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "CairoTransit/7.0.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        trip = data.get("trip", {})
        legs = trip.get("legs", [])
        if legs:
            shape = legs[0].get("shape", "")
            if shape:
                coords = _decode_polyline6(shape)
                if coords:
                    _geometry_cache[cache_key] = coords
                    return coords
    except Exception:
        pass

    return None


def get_road_path(node_path: List[str], nodes: dict) -> List[List[float]]:
    """Get real road geometry for a path of node IDs. Falls back to straight lines."""
    if len(node_path) < 2:
        return []

    full_path = []
    for i in range(len(node_path) - 1):
        from_node = nodes.get(node_path[i])
        to_node = nodes.get(node_path[i + 1])
        if not from_node or not to_node:
            continue

        segment = get_segment_coords(
            from_node['lng'], from_node['lat'],
            to_node['lng'], to_node['lat']
        )

        if segment:
            if full_path and segment and full_path[-1] == segment[0]:
                segment = segment[1:]
            full_path.extend(segment)
        else:
            if not full_path or full_path[-1] != [from_node['lat'], from_node['lng']]:
                full_path.append([from_node['lat'], from_node['lng']])
            full_path.append([to_node['lat'], to_node['lng']])

    return full_path
