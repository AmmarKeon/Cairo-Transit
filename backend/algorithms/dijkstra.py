"""
Dijkstra's Algorithm - Shortest path by cumulative edge weight.
Guarantees optimal path for non-negative weights.
Explores nearest unvisited node first.
"""
import heapq
from typing import Dict, List, Tuple
from .graph import reconstruct_path, calculate_distance, validate_nodes


def find_path(
    graph: Dict[str, List[Tuple[str, float]]],
    start: str,
    goal: str,
    nodes: Dict[str, dict],
) -> dict:
    err = validate_nodes(start, goal, graph)
    if err:
        return {"success": False, "error": err}

    dist = {n: float("inf") for n in graph}
    dist[start] = 0
    parent = {}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d > dist[u]:
            continue
        for v, w in graph.get(u, []):
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    if dist[goal] == float("inf"):
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {
            "nodes": path,
            "distance": dist[goal],
            "algorithm": "Dijkstra",
        },
    }
