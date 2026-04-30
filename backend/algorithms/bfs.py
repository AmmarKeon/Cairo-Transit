"""
Breadth-First Search - Explores by depth level.
Finds path with fewest edges (hops), NOT shortest distance.
Ignores edge weights entirely.
"""
from collections import deque
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

    parent = {}
    visited = {start}
    queue = deque([start])

    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for v, _ in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                queue.append(v)
    else:
        if start != goal:
            return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    dist = calculate_distance(path, graph)
    return {
        "success": True,
        "data": {
            "nodes": path,
            "distance": dist,
            "algorithm": "BFS",
        },
    }
