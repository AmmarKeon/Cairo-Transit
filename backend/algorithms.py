"""GET /api/algorithms"""
from backend.shared import (
    dijkstra, astar, bfs, dfs, greedy,
    bellmanford, bidirectional, randomwalk, mst
)

def handler(request):
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
    ]
