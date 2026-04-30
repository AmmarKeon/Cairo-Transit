"""
A* Search - Heuristic-guided shortest path.
Uses f(n) = g(n) + h(n) where h is straight-line distance to goal.
Faster than Dijkstra while still finding optimal path.
"""
import heapq
from typing import Dict, List, Tuple
from .graph import reconstruct_path, calculate_distance, heuristic, validate_nodes


def find_path(
    graph: Dict[str, List[Tuple[str, float]]],
    start: str,
    goal: str,
    nodes: Dict[str, dict],
) -> dict:
    err = validate_nodes(start, goal, graph)
    if err:
        return {"success": False, "error": err}

    g = {n: float("inf") for n in graph}
    g[start] = 0
    f = {n: float("inf") for n in graph}
    f[start] = heuristic(start, goal, nodes)
    parent = {}
    pq = [(f[start], start)]

    while pq:
        _, u = heapq.heappop(pq)
        if u == goal:
            break
        for v, w in graph.get(u, []):
            ng = g[u] + w
            if ng < g[v]:
                g[v] = ng
                f[v] = ng + heuristic(v, goal, nodes)
                parent[v] = u
                heapq.heappush(pq, (f[v], v))

    if g[goal] == float("inf"):
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {
            "nodes": path,
            "distance": g[goal],
            "algorithm": "A*",
        },
    }
