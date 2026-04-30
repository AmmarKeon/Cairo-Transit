"""
Greedy Best-First Search - Uses ONLY the heuristic to guide search.
Rushes straight toward the goal, ignoring actual edge weights.
Finds paths fast but they are often longer than optimal.
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

    parent = {}
    visited = set()
    pq = [(heuristic(start, goal, nodes), start)]

    while pq:
        _, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u == goal:
            break

        for v, _ in graph.get(u, []):
            if v not in visited:
                parent[v] = u
                heapq.heappush(pq, (heuristic(v, goal, nodes), v))
    else:
        if start != goal and goal not in visited:
            return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    dist = calculate_distance(path, graph)
    return {
        "success": True,
        "data": {
            "nodes": path,
            "distance": dist,
            "algorithm": "Greedy Best-First",
        },
    }
