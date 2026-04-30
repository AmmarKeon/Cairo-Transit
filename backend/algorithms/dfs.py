"""
Depth-First Search - Explores as deep as possible before backtracking.
Produces winding, non-optimal paths that visit many nodes.
NOT suitable for shortest path - finds ANY path.
"""
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
    stack = [start]

    while stack:
        u = stack.pop()
        if u == goal:
            break
        # Reverse neighbors for consistent exploration order
        for v, _ in reversed(graph.get(u, [])):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                stack.append(v)
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
            "algorithm": "DFS",
        },
    }
