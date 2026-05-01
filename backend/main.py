"""
Cairo Transit API v6 - Modular algorithms, real OSM road geometries via Valhalla
"""

import os
import logging
import threading
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import urllib.request
import urllib.error
import json
import csv

# Import modular algorithms
from algorithms import (
    dijkstra, astar, bfs, dfs, greedy,
    bellmanford, bidirectional, randomwalk, find_mst
)

# ─── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── App Setup ──────────────────────────────────────────────────────────────────

app = FastAPI(title="Cairo Transit API", version="6.0.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import atexit

@app.on_event("startup")
def startup_prefetch():
    """Pre-fetch road geometry for all graph edges in background thread."""
    def _prefetch():
        uncached = 0
        for a, b, _ in ROADS:
            na, nb = NODES.get(a), NODES.get(b)
            if na and nb:
                seg = get_road_segment(na['lng'], na['lat'], nb['lng'], nb['lat'])
                if seg is None:
                    uncached += 1
        logger.info(f"Pre-fetch complete: {_road_cache.size} cached segments, {uncached} failed")
        _road_cache.save_if_dirty()
    threading.Thread(target=_prefetch, daemon=True).start()

@app.on_event("shutdown")
def shutdown_event():
    """Save road geometry cache on server shutdown."""
    logger.info(f"Shutting down, saving {_road_cache.size} cached road segments...")
    _road_cache.save_if_dirty()

DATA_DIR = Path(__file__).parent.parent / "data"

# Valhalla URL - only allow pre-approved public servers to prevent SSRF
_ALLOWED_VALHALLA_HOSTS = {
    "valhalla1.openstreetmap.de",
    "valhalla2.openstreetmap.de",
    "valhalla3.openstreetmap.de",
}
_valhalla_env = os.getenv("VALHALLA_URL", "").strip()
if _valhalla_env:
    from urllib.parse import urlparse
    _parsed = urlparse(_valhalla_env)
    if _parsed.hostname not in _ALLOWED_VALHALLA_HOSTS:
        raise ValueError(f"VALHALLA_URL hostname '{_parsed.hostname}' not in allowlist")
    VALHALLA_URL = _valhalla_env
else:
    VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"

CACHE_DIR = Path(__file__).parent / ".road_cache"
CACHE_FILE = CACHE_DIR / "valhalla_segments.json"

# ─── Data Loading ───────────────────────────────────────────────────────────────

def load_nodes(filepath: str) -> Dict[str, dict]:
    nodes = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'ID' not in row or 'Name' not in row:
                    logger.warning(f"Skipping malformed row in {filepath}: {row}")
                    continue
                node_id = row['ID']
                if node_id in nodes:
                    logger.warning(f"Duplicate node ID '{node_id}' in {filepath}, skipping")
                    continue
                try:
                    nodes[node_id] = {
                        "id": node_id,
                        "name": row['Name'],
                        "lat": float(row['Y-coordinate']),
                        "lng": float(row['X-coordinate']),
                        "type": row.get('Type', 'Unknown'),
                    }
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing row {row} in {filepath}: {e}")
    except FileNotFoundError:
        logger.error(f"Data file not found: {filepath}")
    return nodes

def load_roads(nodes: Dict[str, dict]) -> List[Tuple[str, str, float]]:
    roads = []
    try:
        with open(DATA_DIR / "existing_roads.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    from_id = row['FromID']
                    to_id = row['ToID']
                    distance = float(row['Distance(km)'])
                    if from_id not in nodes:
                        logger.warning(f"Road references unknown node '{from_id}', skipping")
                        continue
                    if to_id not in nodes:
                        logger.warning(f"Road references unknown node '{to_id}', skipping")
                        continue
                    roads.append((from_id, to_id, distance))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing road row {row}: {e}")
    except FileNotFoundError:
        logger.error("Roads data file not found")
    return roads

NODES = {**load_nodes(DATA_DIR / "neighborhoods.csv"), **load_nodes(DATA_DIR / "facilities.csv")}
ROADS = load_roads(NODES)

# Build neighbors graph with real distances from CSV
GRAPH: Dict[str, List[Tuple[str, float]]] = {}
for a, b, dist in ROADS:
    if a not in GRAPH: GRAPH[a] = []
    if b not in GRAPH: GRAPH[b] = []
    GRAPH[a].append((b, dist))
    GRAPH[b].append((a, dist))

logger.info(f"Loaded {len(NODES)} nodes, {len(ROADS)} roads, {len(GRAPH)} graph vertices")

# ─── Road Geometry Stats ──────────────────────────────────────────────────────

_road_stats = {"success": 0, "failed": 0, "cached": 0}

# ─── Road Geometry Cache ────────────────────────────────────────────────────────

class RoadGeometryCache:
    """Thread-safe persistent disk cache for road geometry segments."""

    def __init__(self, cache_file: Path):
        self._cache_file = cache_file
        self._lock = threading.Lock()
        self._memory: Dict[str, List[List[float]]] = {}
        self._dirty = False
        self._load()

    def _cache_key(self, from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> str:
        # Symmetric key: sort coordinates so A→B and B→A share the same cache entry
        a = f"{round(from_lng, 6)},{round(from_lat, 6)}"
        b = f"{round(to_lng, 6)},{round(to_lat, 6)}"
        if a < b:
            return f"{a};{b}"
        return f"{b};{a}"

    def _load(self):
        """Load cached segments from disk."""
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._memory = data
                logger.info(f"Loaded {len(self._memory)} cached road segments from disk")
            else:
                logger.info("No road geometry cache found, starting fresh")
        except Exception as e:
            logger.warning(f"Failed to load road cache: {e}")
            self._memory = {}

    def _save(self):
        """Persist cache to disk (called lazily)."""
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._memory, f)
        except Exception as e:
            logger.warning(f"Failed to save road cache: {e}")
        finally:
            with self._lock:
                self._dirty = False

    def get(self, from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[List[List[float]]]:
        key = self._cache_key(from_lng, from_lat, to_lng, to_lat)
        with self._lock:
            return self._memory.get(key)

    def put(self, from_lng: float, from_lat: float, to_lng: float, to_lat: float, coords: List[List[float]]):
        key = self._cache_key(from_lng, from_lat, to_lng, to_lat)
        with self._lock:
            if key not in self._memory:
                self._memory[key] = coords
                self._dirty = True
                # Save periodically (every 50 new entries) in background
                if len(self._memory) % 50 == 0:
                    threading.Thread(target=self._save, daemon=True).start()

    def save_if_dirty(self):
        with self._lock:
            if self._dirty:
                threading.Thread(target=self._save, daemon=True).start()
                # Give the thread a moment to grab the lock
                self._dirty = False

    @property
    def size(self) -> int:
        return len(self._memory)

_road_cache = RoadGeometryCache(CACHE_FILE)

# ─── Valhalla Road Geometry ─────────────────────────────────────────────────────

import time

class _RateLimiter:
    """Simple rate limiter to avoid 429s from Valhalla."""
    def __init__(self, min_interval: float = 0.1):
        self._min_interval = min_interval
        self._last_call = 0.0
        self._lock = threading.Lock()

    def wait(self):
        sleep_time = 0.0
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                sleep_time = self._min_interval - elapsed
            self._last_call = now + sleep_time
        if sleep_time > 0:
            time.sleep(sleep_time)

_valhalla_limiter = _RateLimiter(min_interval=0.15)

def _decode_polyline6(encoded: str) -> List[List[float]]:
    """Decode a precision-6 encoded polyline (Valhalla format) to [[lat, lng], ...]."""
    coords = []
    index = 0
    lat = 0
    lng = 0
    while index < len(encoded):
        # Decode latitude
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

        # Decode longitude
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


def _fetch_valhalla_raw(from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[str]:
    """Fetch a single road segment from Valhalla API (no caching). Returns JSON-encoded coords or None."""
    payload = json.dumps({
        "locations": [
            {"lat": from_lat, "lon": from_lng},
            {"lat": to_lat, "lon": to_lng}
        ],
        "costing": "auto",
        "directions_options": {"units": "kilometers"}
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CairoTransit/6.0.0"
    }

    max_retries = 3
    for attempt in range(max_retries):
        _valhalla_limiter.wait()
        try:
            req = urllib.request.Request(VALHALLA_URL, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())

            trip = data.get("trip", {})
            legs = trip.get("legs", [])
            if legs:
                shape = legs[0].get("shape", "")
                if shape:
                    coords = _decode_polyline6(shape)
                    if coords:
                        return json.dumps(coords)
            # Valhalla returned valid JSON but no shape — segment may not exist
            logger.warning(f"Valhalla returned no shape for ({from_lat},{from_lng})->({to_lat},{to_lng})")
            return None

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 1.0 * (attempt + 1)
                logger.info(f"Valhalla rate limited (attempt {attempt+1}/{max_retries}), waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                logger.warning(f"Valhalla HTTP {e.code} for ({from_lat},{from_lng})->({to_lat},{to_lng}): {e}")
                return None
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
            wait = 0.5 * (attempt + 1)
            logger.warning(f"Valhalla error (attempt {attempt+1}/{max_retries}): {e}, retrying in {wait}s...")
            time.sleep(wait)
            continue

    logger.error(f"Valhalla failed after {max_retries} attempts for ({from_lat},{from_lng})->({to_lat},{to_lng})")
    return None


# In-memory cache that skips None values (unlike lru_cache which caches everything)
_valhalla_memory: Dict[str, Optional[str]] = {}

def _cached_valhalla_segment(from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[str]:
    """Fetch road segment with in-memory cache. Does NOT cache failures."""
    key = f"{round(from_lng,6)},{round(from_lat,6)};{round(to_lng,6)},{round(to_lat,6)}"

    # Check in-memory cache (skip if None = previous failure)
    if key in _valhalla_memory:
        return _valhalla_memory[key]

    result = _fetch_valhalla_raw(from_lng, from_lat, to_lng, to_lat)

    # Only cache successes — allow retries on next request if it failed
    if result is not None:
        _valhalla_memory[key] = result

    return result


def get_road_segment(from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[List[List[float]]]:
    """Get real road geometry for a segment. Checks disk cache first, then Valhalla API."""
    # Round coordinates upfront for consistent cache keys
    from_lng = round(from_lng, 6)
    from_lat = round(from_lat, 6)
    to_lng = round(to_lng, 6)
    to_lat = round(to_lat, 6)

    # 1. Check disk cache
    cached = _road_cache.get(from_lng, from_lat, to_lng, to_lat)
    if cached is not None:
        _road_stats["cached"] += 1
        return cached

    # 2. Call Valhalla API (forward direction)
    result_json = _cached_valhalla_segment(from_lng, from_lat, to_lng, to_lat)
    if result_json:
        coords = json.loads(result_json)
        _road_cache.put(from_lng, from_lat, to_lng, to_lat, coords)
        _road_stats["success"] += 1
        return coords

    # 3. Try reverse direction (roads are symmetric)
    result_json_rev = _cached_valhalla_segment(to_lng, to_lat, from_lng, from_lat)
    if result_json_rev:
        coords = json.loads(result_json_rev)
        coords = coords[::-1]  # Reverse the path
        _road_cache.put(from_lng, from_lat, to_lng, to_lat, coords)
        _road_stats["success"] += 1
        return coords

    # 4. Both directions failed — log and return None (straight line fallback)
    _road_stats["failed"] += 1
    logger.warning(f"No road geometry for ({from_lat},{from_lng})->({to_lat},{to_lng}), using straight line")
    return None


def get_real_road_path(node_path: List[str]) -> List[List[float]]:
    """Get real road geometry for a path of node IDs using Valhalla with disk cache."""
    if len(node_path) < 2:
        return []

    full_path = []
    for i in range(len(node_path) - 1):
        from_node = NODES.get(node_path[i])
        to_node = NODES.get(node_path[i + 1])
        if not from_node or not to_node:
            continue

        segment = get_road_segment(from_node['lng'], from_node['lat'], to_node['lng'], to_node['lat'])

        if segment:
            # Deduplicate consecutive identical points
            if full_path and segment and full_path[-1] == segment[0]:
                segment = segment[1:]
            full_path.extend(segment)
        else:
            # Fallback: straight line between the two nodes
            if not full_path or full_path[-1] != [from_node['lat'], from_node['lng']]:
                full_path.append([from_node['lat'], from_node['lng']])
            full_path.append([to_node['lat'], to_node['lng']])

    # Persist any new cache entries
    _road_cache.save_if_dirty()

    return full_path

# ─── Helper: Run algorithm and add real road path ───────────────────────────────

def run_algo(algo_fn, start: str, goal: str, **kwargs) -> dict:
    """Run an algorithm function and add real road geometry to the result."""
    result = algo_fn(GRAPH, start, goal, NODES, **kwargs)
    if result.get("success") and "data" in result:
        node_ids = result["data"].get("nodes", [])
        result["data"]["path"] = get_real_road_path(node_ids)
        result["data"]["from"] = start
        result["data"]["to"] = goal
    return result

# ─── API Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Cairo Transit API v6",
        "algorithms": [
            "dijkstra", "astar", "bfs", "valhalla", "dfs", "greedy",
            "randomwalk", "bellmanford", "bidirectional"
        ],
        "features": ["real_road_geometries", "osm_routing", "modular_algorithms", "persistent_cache"]
    }

@app.get("/api/nodes")
def get_nodes():
    return list(NODES.values())

@app.get("/api/roads")
def get_roads():
    return [{"from": a, "to": b, "distance": d} for a, b, d in ROADS]

# ─── Route Endpoints (all use modular algorithms) ──────────────────────────────

@app.get("/api/route/dijkstra")
def dijkstra_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(dijkstra, start, goal)

@app.get("/api/route/astar")
def astar_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(astar, start, goal)

@app.get("/api/route/bfs")
def bfs_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(bfs, start, goal)

@app.get("/api/route/dfs")
def dfs_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(dfs, start, goal)

@app.get("/api/route/greedy")
def greedy_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(greedy, start, goal)

@app.get("/api/route/bellmanford")
def bellmanford_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(bellmanford, start, goal)

@app.get("/api/route/bidirectional")
def bidirectional_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(bidirectional, start, goal)

@app.get("/api/route/randomwalk")
def randomwalk_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    return run_algo(randomwalk, start, goal)

@app.get("/api/route/osrm")
def osrm_route(
    start: str = Query(..., min_length=1, max_length=100),
    goal: str = Query(..., min_length=1, max_length=100)
):
    """Valhalla routing endpoint - real OSM road geometry."""
    if start not in NODES or goal not in NODES:
        return {"success": False, "error": "Invalid nodes"}

    s, e = NODES[start], NODES[goal]
    segment = get_road_segment(s['lng'], s['lat'], e['lng'], e['lat'])

    if segment:
        return {
            "success": True,
            "data": {
                "path": segment,
                "from": s['name'],
                "to": e['name'],
                "algorithm": "Valhalla (OSM)"
            }
        }
    return {"success": False, "error": "No route found"}


@app.get("/api/cache/stats")
def cache_stats():
    """Return road geometry cache statistics."""
    return {
        "cached_segments": _road_cache.size,
        "cache_file": str(CACHE_FILE),
        "stats": _road_stats,
        "total_graph_edges": len(ROADS),
    }

# ─── Network Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/network/mst")
def get_mst():
    result = find_mst(GRAPH, NODES)
    return result

# ─── Coming Soon Endpoints ─────────────────────────────────────────────────────

@app.get("/api/route/time-varying")
def time_varying_route(start: str = Query(...), goal: str = Query(...)):
    return {"success": False, "error": "Not implemented yet", "algorithm": "Time-Varying Shortest Path"}

@app.get("/api/route/dp-scheduling")
def dp_scheduling_route():
    return {"success": False, "error": "Not implemented yet", "algorithm": "DP Transit Scheduling"}

@app.get("/api/route/dp-allocation")
def dp_allocation_route():
    return {"success": False, "error": "Not implemented yet", "algorithm": "DP Resource Allocation"}

@app.get("/api/route/dp-memoization")
def dp_memoization_route(start: str = Query(...), goal: str = Query(...)):
    return {"success": False, "error": "Not implemented yet", "algorithm": "Memoized Route Planning"}

@app.get("/api/route/greedy-signals")
def greedy_signals_route():
    return {"success": False, "error": "Not implemented yet", "algorithm": "Greedy Signal Optimization"}

@app.get("/api/route/greedy-preemption")
def greedy_preemption_route(start: str = Query(...), goal: str = Query(...)):
    return {"success": False, "error": "Not implemented yet", "algorithm": "Emergency Vehicle Preemption"}

# ─── Algorithm Info ────────────────────────────────────────────────────────────

@app.get("/api/algorithms")
def get_algorithms():
    return [
        {
            "key": "mst", "name": "Minimum Spanning Tree (Kruskal's)",
            "description": "Designs cost-efficient road networks connecting all areas while minimizing total construction cost.",
            "complexity": "O(E log E)", "color": "#1a3a3a", "icon": "network", "category": "mst", "implemented": True
        },
        {
            "key": "dijkstra", "name": "Dijkstra's Algorithm",
            "description": "Finds the shortest path by exploring the nearest unvisited node first. Guarantees optimal solution.",
            "complexity": "O((V + E) log V)", "color": "#22c55e", "icon": "route", "category": "shortest-path", "implemented": True
        },
        {
            "key": "astar", "name": "A* Search",
            "description": "Uses a heuristic to guide search toward the goal. Faster than Dijkstra while still finding the optimal path.",
            "complexity": "O((V + E) log V)", "color": "#8b5cf6", "icon": "zap", "category": "shortest-path", "implemented": True
        },
        {
            "key": "bfs", "name": "Breadth-First Search",
            "description": "Explores all nodes at current depth before moving deeper. Finds path with fewest edges, not shortest distance.",
            "complexity": "O(V + E)", "color": "#eab308", "icon": "layers", "category": "shortest-path", "implemented": True
        },
        {
            "key": "osrm", "name": "Valhalla (OSM) Routing",
            "description": "Uses OpenStreetMap data via Valhalla router for actual driving routes with real road geometry.",
            "complexity": "Real-world", "color": "#3b82f6", "icon": "navigation", "category": "shortest-path", "implemented": True
        },
        {
            "key": "dfs", "name": "Depth-First Search",
            "description": "Explores as deep as possible before backtracking. Produces winding, non-optimal paths.",
            "complexity": "O(V + E)", "color": "#0ea5e9", "icon": "layers", "category": "shortest-path", "implemented": True
        },
        {
            "key": "greedy", "name": "Greedy Best-First Search",
            "description": "Uses only the heuristic (straight-line distance) to guide search. Rushes toward goal but finds longer paths.",
            "complexity": "O((V + E) log V)", "color": "#f43f5e", "icon": "zap", "category": "shortest-path", "implemented": True
        },
        {
            "key": "randomwalk", "name": "Random Walk",
            "description": "Randomly picks next neighbors with bias toward goal. Produces chaotic, inefficient paths.",
            "complexity": "O(n)", "color": "#a855f7", "icon": "shuffle", "category": "shortest-path", "implemented": True
        },
        {
            "key": "bellmanford", "name": "Bellman-Ford Algorithm",
            "description": "Relaxes edges V-1 times in input order. Can handle negative weights.",
            "complexity": "O(V * E)", "color": "#14b8a6", "icon": "refresh-cw", "category": "shortest-path", "implemented": True
        },
        {
            "key": "bidirectional", "name": "Bidirectional Dijkstra",
            "description": "Searches simultaneously from both start and goal. Meets in the middle.",
            "complexity": "O((V + E) log V)", "color": "#ec4899", "icon": "arrow-left-right", "category": "shortest-path", "implemented": True
        },
        {
            "key": "time-varying", "name": "Time-Varying Shortest Path",
            "description": "Modified Dijkstra accounting for Cairo's rush hour traffic conditions.",
            "complexity": "O((V + E) log V)", "color": "#f97316", "icon": "timer", "category": "shortest-path", "implemented": False
        },
        {
            "key": "dp-scheduling", "name": "DP Transit Scheduling",
            "description": "Dynamic programming for optimal scheduling of public transportation vehicles.",
            "complexity": "O(n^2 * t)", "color": "#3b82f6", "icon": "calendar", "category": "dynamic-programming", "implemented": False
        },
        {
            "key": "dp-allocation", "name": "DP Resource Allocation",
            "description": "Dynamic programming for road maintenance budget optimization.",
            "complexity": "O(n * W)", "color": "#06b6d4", "icon": "dollar-sign", "category": "dynamic-programming", "implemented": False
        },
        {
            "key": "dp-memoization", "name": "Memoized Route Planning",
            "description": "Memoization techniques to improve route planning performance.",
            "complexity": "O(V + E)", "color": "#8b5cf6", "icon": "cpu", "category": "dynamic-programming", "implemented": False
        },
        {
            "key": "greedy-signals", "name": "Greedy Signal Optimization",
            "description": "Greedy approach for real-time traffic signal optimization.",
            "complexity": "O(n log n)", "color": "#eab308", "icon": "traffic-cone", "category": "greedy", "implemented": False
        },
        {
            "key": "greedy-preemption", "name": "Emergency Vehicle Preemption",
            "description": "Priority-based emergency vehicle preemption during high congestion.",
            "complexity": "O(n)", "color": "#ef4444", "icon": "siren", "category": "greedy", "implemented": False
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
