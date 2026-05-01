# Cairo Transit

Graph algorithm visualization tool for Greater Cairo's transportation network. Implements Dijkstra, A*, BFS, DFS, and more on a real OpenStreetMap backend.

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Setup

```bash
git clone https://github.com/AmmarKeon/Cairo-Transit.git
cd Cairo-Transit
git checkout Keon0.2

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Run

**Windows:**
```
scripts\run_server.bat
```

**Manual:**
```bash
# Terminal 1 — Backend (port 8000)
cd backend
python main.py

# Terminal 2 — Frontend (port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server
│   └── algorithms/          # Dijkstra, A*, BFS, DFS, etc.
├── frontend/
│   └── src/App.jsx          # React + Leaflet map UI
├── data/
│   ├── neighborhoods.csv    # 25 neighborhood nodes
│   ├── facilities.csv       # 20 facility nodes
│   └── existing_roads.csv   # 166 road edges
├── scripts/                 # Dev scripts (run, test)
├── tests/                   # Pytest tests
├── docs/ARCHITECTURE.md     # Full architecture guide
└── requirements.txt         # Python deps
```

## What It Does

1. Pick two locations on the map (neighborhoods, hospitals, airports, etc.)
2. Choose an algorithm (Dijkstra, A*, BFS, Random Walk, etc.)
3. See the route drawn on real Cairo roads via OpenStreetMap/Valhalla

## Algorithms

| Algorithm | Complexity | Notes |
|-----------|-----------|-------|
| Dijkstra | O((V+E) log V) | Optimal shortest path |
| A* | O((V+E) log V) | Heuristic-guided, faster |
| BFS | O(V+E) | Fewest hops, not shortest distance |
| DFS | O(V+E) | Deep exploration, non-optimal |
| Greedy Best-First | O((V+E) log V) | Rushes toward goal |
| Bellman-Ford | O(V·E) | Handles negative weights |
| Bidirectional Dijkstra | O((V+E) log V) | Searches from both ends |
| Random Walk | O(n) | Chaotic, shows why we need proper algos |
| Kruskal's MST | O(E log E) | Minimum spanning tree |

## Tech Stack

- **Frontend:** React 18, Vite, Leaflet, Tailwind CSS
- **Backend:** Python, FastAPI, Uvicorn
- **Routing:** Valhalla (OpenStreetMap) for real road geometry

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full breakdown — data flow, how the map connects to the backend, algorithm module design, and notes for AI agents.
