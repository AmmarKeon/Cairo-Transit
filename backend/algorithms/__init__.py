"""
Cairo Transit Algorithm Suite
=============================
Modular implementations of pathfinding and graph algorithms.

Each algorithm module exposes:
    find_path(graph, start, goal, nodes) -> dict

Where:
    graph: Dict[str, List[Tuple[str, float]]]  - adjacency list with weights
    start: str  - start node ID
    goal: str  - goal node ID
    nodes: Dict[str, dict]  - node data (id, name, lat, lng, type)

Returns:
    {"success": True, "data": {"path": [...], "nodes": [...], "distance": float, "algorithm": str}}
    or {"success": False, "error": str}
"""

from .dijkstra import find_path as dijkstra
from .astar import find_path as astar
from .bfs import find_path as bfs
from .dfs import find_path as dfs
from .greedy import find_path as greedy
from .bellmanford import find_path as bellmanford
from .bidirectional import find_path as bidirectional
from .randomwalk import find_path as randomwalk
from .mst import find_mst

__all__ = [
    "dijkstra", "astar", "bfs", "dfs", "greedy",
    "bellmanford", "bidirectional", "randomwalk", "find_mst"
]
