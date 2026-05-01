# Cairo Transit - Architecture Guide

> **For AI agents and new developers.** This document explains how the frontend and backend work together, the data flow, and the current state of the project.

---

## Project Overview

Cairo Transit is a **graph algorithm visualization tool** for Greater Cairo's transportation network. It implements pathfinding algorithms (Dijkstra, A*, BFS, DFS, etc.) and renders routes on a real OpenStreetMap map using **Leaflet**.

**Stack:**
- **Frontend:** React 18 + Vite + Tailwind CSS + Leaflet (port 5173)
- **Backend:** Python FastAPI + Uvicorn (port 8000)
- **Routing:** Valhalla (OpenStreetMap) for real road geometry

---

## Directory Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI server (all API endpoints)
│   ├── requirements.txt     # Python deps for backend
│   ├── algorithms/          # Modular algorithm implementations
│   │   ├── __init__.py      # Exports all algorithms
│   │   ├── dijkstra.py
│   │   ├── astar.py
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   ├── greedy.py
│   │   ├── bellmanford.py
│   │   ├── bidirectional.py
│   │   ├── randomwalk.py
│   │   ├── mst.py
│   │   └── graph.py         # Shared graph utilities (heuristic, distance calc)
│   └── .road_cache/         # Persistent Valhalla geometry cache (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component (entire UI in one file)
│   │   ├── index.css        # All styles (Tailwind + custom CSS)
│   │   └── main.jsx         # React entry point
│   ├── index.html
│   ├── vite.config.js       # Vite config with /api proxy to backend
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
│
├── data/
│   ├── neighborhoods.csv    # 25 neighborhood nodes (ID, Name, coordinates, Type)
│   ├── facilities.csv       # 20 facility nodes (hospitals, airports, etc.)
│   └── existing_roads.csv   # 166 edges (FromID, ToID, Distance in km)
│
├── scripts/
│   ├── run_server.bat       # Starts both backend + frontend (Windows)
│   ├── run_server.py        # Starts backend only + tests endpoints
│   ├── run_all.py           # Starts both servers (Python version)
│   ├── test_algo.py         # Quick algorithm test
│   ├── test_all.py          # Tests all API endpoints
│   ├── test_api.py          # Tests nodes + route endpoints
│   └── test_routes.py       # Tests all route algorithms
│
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py
│   └── test_graph_core.py
│
├── docs/
│   └── ARCHITECTURE.md      # This file
│
├── requirements.txt         # Root Python deps (same as backend)
└── README.md
```

---

## How the Frontend Works

### Single-File Architecture

The entire frontend lives in **`frontend/src/App.jsx`** (~1300 lines). It contains:

1. **Splash Screen** — animated loading screen shown for ~2.8 seconds
2. **Hero Section** — title, description, static map preview with first 20 nodes
3. **About Section** — project overview with 4 algorithm category cards
4. **Algorithms Section** — grid of all 16 algorithm cards (9 implemented, 7 "Coming Soon")
5. **Map Section** — embedded Leaflet map with inline controls
6. **Fullscreen Map Overlay** — modal dialog with sidebar controls + full map

### Key Components (all in App.jsx)

| Component | Purpose |
|-----------|---------|
| `ErrorBoundary` | Catches React errors, shows reload button |
| `SplashScreen` | Animated intro (auto-dismisses after 2.8s) |
| `AlgorithmCard` | Card for each algorithm with icon, description, complexity |
| `SearchBox` | Autocomplete search for nodes (filters by name) |
| `MapFlyTo` | Leaflet hook to animate map to a position |
| `MapControls` | Sidebar with Point A/B search, algorithm picker, "Show Path" button |
| `RouteInfo` | Displays route stats (distance, node count) after computation |
| `AppContent` | Main component that orchestrates everything |

### State Management

All state is in `AppContent` using React `useState`:

```
- showSplash: boolean       — controls splash screen visibility
- nodes: object             — node ID → node data map (from /api/nodes)
- nodeList: array           — same data as array for iteration
- pointA: object|null       — selected start node
- pointB: object|null       — selected end node
- selectedAlgo: string|null — algorithm key (e.g., 'dijkstra', 'astar')
- routePath: array          — [[lat, lng], ...] coordinates for polyline
- routeData: object|null    — route metadata (distance, algorithm name, nodes)
- loading: boolean          — true while API call is in progress
- error: string|null        — error message to display
- isFullscreen: boolean     — whether fullscreen map overlay is open
- flyTo: object|null        — {position: [lat, lng], zoom: number} for map animation
- visibleSections: Set      — tracks which sections are visible (scroll animation)
```

### How the Map Works

1. **On load:** Frontend fetches `GET /api/nodes` to get all 45 nodes
2. **Nodes render as markers** on the Leaflet map using `createIcon(type)` — custom SVG markers colored by node type (Medical=red, Transit=dark, Education=purple, etc.)
3. **User selects Point A and Point B** via `SearchBox` components (autocomplete search)
4. **User picks an algorithm** from the radio button list
5. **User clicks "Show Path":**
   - Frontend sends `GET /api/route/{algorithm}?start={id}&goal={id}`
   - Backend runs the algorithm, fetches real road geometry from Valhalla, returns coordinate path
   - Frontend renders the path as a `<Polyline>` on the map
   - Map flies to the midpoint of the route
   - If not already in fullscreen, opens the fullscreen overlay

### Map Rendering Details

- **Tile source:** OpenStreetMap (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`)
- **Center:** `[30.0444, 31.2357]` (Cairo, Egypt)
- **Default zoom:** 12
- **Markers:** Custom `L.divIcon` with SVG pin, colored by `typeColors` map
- **Route polyline:** `<Polyline>` with algorithm-specific color, weight 5, opacity 0.8
- **Two maps exist:** one embedded in the page, one in the fullscreen overlay. They share state but are separate `<MapContainer>` instances.

---

## How the Backend Works

### FastAPI Server (`backend/main.py`)

The backend is a single FastAPI file that:

1. **Loads data on startup:**
   - Reads `data/neighborhoods.csv` and `data/facilities.csv` → `NODES` dict (45 nodes)
   - Reads `data/existing_roads.csv` → `ROADS` list (166 edges)
   - Builds `GRAPH` adjacency list: `{node_id: [(neighbor_id, distance_km), ...]}`

2. **Serves API endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check, lists features |
| `/api/nodes` | GET | Returns all 45 nodes |
| `/api/roads` | GET | Returns all 166 edges |
| `/api/algorithms` | GET | Returns algorithm metadata (for frontend) |
| `/api/route/{algo}` | GET | Runs algorithm, returns path with real road geometry |
| `/api/network/mst` | GET | Runs Kruskal's MST |
| `/api/cache/stats` | GET | Returns Valhalla cache statistics |

3. **Algorithm routing:**
   - Each `/api/route/{algo}` endpoint calls `run_algo(algo_fn, start, goal)`
   - `run_algo` runs the algorithm, then calls `get_real_road_path(node_ids)` to get real road geometry
   - The algorithm returns node IDs; Valhalla converts them to actual road coordinates

### Algorithm Module (`backend/algorithms/`)

Each algorithm is a separate file with a `find_path(graph, start, goal, nodes)` function:

```python
# Standard signature for all algorithms:
def find_path(
    graph: Dict[str, List[Tuple[str, float]]],  # adjacency list
    start: str,                                   # start node ID
    goal: str,                                    # goal node ID
    nodes: Dict[str, dict],                       # node data
    **kwargs                                      # algorithm-specific params
) -> dict:
    # Returns:
    # {"success": True, "data": {"path": [...], "nodes": [...], "distance": float, "algorithm": str}}
    # or {"success": False, "error": str}
```

The `graph.py` module provides shared utilities:
- `calculate_distance(lat1, lng1, lat2, lng2)` — Haversine formula
- `heuristic(node1, node2)` — straight-line distance estimate
- `reconstruct_path(came_from, current)` — backtrack from goal to start
- `validate_nodes(graph, start, goal)` — check nodes exist

### Valhalla Road Geometry

This is the key feature that makes routes look real on the map:

1. **Algorithm returns:** list of node IDs like `["F2", "5", "F9"]`
2. **`get_real_road_path(node_ids)`** iterates consecutive pairs
3. **For each pair:** calls `get_road_segment(from_lng, from_lat, to_lng, to_lat)`
4. **Cache check:** looks in `RoadGeometryCache` (in-memory + disk at `.road_cache/valhalla_segments.json`)
5. **If not cached:** calls Valhalla API (`https://valhalla1.openstreetmap.de/route`)
6. **Valhalla returns:** encoded polyline (precision 6) → decoded to `[[lat, lng], ...]`
7. **Result:** ~100-1000+ coordinate points per segment (real road curves)

**Cache features:**
- Symmetric keys (A→B and B→A share cache entry)
- Thread-safe with `threading.Lock`
- Saves to disk every 50 new entries + on server shutdown
- LRU in-memory cache (2048 entries)

**Rate limiting:** 150ms minimum between Valhalla calls, with 429 retry (1s delay).

---

## Data Flow: User Click → Route on Map

```
User clicks "Show Path"
    │
    ▼
Frontend: GET /api/route/dijkstra?start=F2&goal=F9
    │
    ▼
Backend: run_algo(dijkstra, "F2", "F9")
    │
    ├─ dijkstra.find_path(GRAPH, "F2", "F9", NODES)
    │   → {"success": true, "data": {"nodes": ["F2", "5", "F9"], "distance": 4.2, ...}}
    │
    ├─ get_real_road_path(["F2", "5", "F9"])
    │   ├─ get_road_segment(F2.lng, F2.lat, 5.lng, 5.lat)
    │   │   ├─ Check disk cache → miss
    │   │   ├─ Call Valhalla API → get encoded polyline
    │   │   ├─ Decode → [[30.04, 31.23], [30.05, 31.24], ...]  (200+ points)
    │   │   └─ Save to cache
    │   │
    │   ├─ get_road_segment(5.lng, 5.lat, F9.lng, F9.lat)
    │   │   └─ (same process)
    │   │
    │   └─ Combine segments → full path [[lat, lng], ...]
    │
    └─ Return JSON with path coordinates
    │
    ▼
Frontend: setRoutePath(data.data.path)
    │
    ▼
Leaflet: <Polyline positions={routePath} /> renders on map
```

---

## Implemented vs Coming Soon

### Implemented (9 algorithms)
| Key | Algorithm | What it does |
|-----|-----------|--------------|
| `dijkstra` | Dijkstra's | Optimal shortest path |
| `astar` | A* Search | Heuristic-guided shortest path |
| `bfs` | Breadth-First Search | Fewest edges path |
| `dfs` | Depth-First Search | Deep exploration (non-optimal) |
| `greedy` | Greedy Best-First | Heuristic-only (non-optimal) |
| `bellmanford` | Bellman-Ford | Edge relaxation order |
| `bidirectional` | Bidirectional Dijkstra | Meet-in-the-middle |
| `randomwalk` | Random Walk | Random neighbor selection |
| `mst` | Kruskal's MST | Minimum spanning tree (network, not route) |
| `osrm` | Valhalla Routing | Real OSM driving route (single segment) |

### Coming Soon (6 algorithms)
| Key | Algorithm | Category |
|-----|-----------|----------|
| `time-varying` | Time-Varying Shortest Path | Shortest Path |
| `dp-scheduling` | DP Transit Scheduling | Dynamic Programming |
| `dp-allocation` | DP Resource Allocation | Dynamic Programming |
| `dp-memoization` | Memoized Route Planning | Dynamic Programming |
| `greedy-signals` | Greedy Signal Optimization | Greedy |
| `greedy-preemption` | Emergency Vehicle Preemption | Greedy |

---

## Running the Project

### Quick Start (Windows)
```bash
scripts\run_server.bat
```
This starts both backend (port 8000) and frontend (port 5173).

### Manual Start
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Install Dependencies
```bash
# Python
pip install -r requirements.txt

# Node.js
cd frontend && npm install
```

---

## Key Configuration

| Setting | Default | Source |
|---------|---------|--------|
| Backend port | 8000 | `backend/main.py` (uvicorn) |
| Frontend port | 5173 | `frontend/vite.config.js` |
| API base URL | `http://localhost:8000` | `frontend/src/App.jsx` (VITE_API_URL env) |
| Valhalla URL | `https://valhalla1.openstreetmap.de/route` | `backend/main.py` (VALHALLA_URL env) |
| CORS origins | `http://localhost:5173` | `backend/main.py` (ALLOWED_ORIGINS env) |

---

## Notes for AI Agents

- **All frontend code is in one file** (`App.jsx`). When modifying UI, you only need to edit this one file.
- **All backend code is in one file** (`main.py`) plus the `algorithms/` module. Algorithm implementations are isolated.
- **The frontend proxies `/api` to backend** via Vite's dev server proxy. No CORS issues in development.
- **Valhalla calls are rate-limited** (150ms between calls). Don't bypass this or you'll get 429 errors.
- **Road geometry is cached on disk** at `backend/.road_cache/valhalla_segments.json`. This file grows over time. It's gitignored.
- **Node IDs** are strings like `"F2"`, `"57357"`, `"ramses"`. They come from CSV files.
- **The `/api/route/osrm` endpoint** is actually Valhalla (legacy name). It does single-segment routing, not full pathfinding.
- **MST is a network visualization**, not a route. It returns edges, not a path between two nodes.
