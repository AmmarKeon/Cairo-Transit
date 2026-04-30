"""
Bellman-Ford Algorithm - Relaxes all edges V-1 times.
Processes edges in input order (not sorted by distance).
Can handle negative weights (though we don't have any).
Same shortest distances as Dijkstra but different exploration pattern.
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

    # Build edge list from graph
    edges = []
    seen = set()
    for u, neighbors in graph.items():
        for v, w in neighbors:
            if (u, v) not in seen and (v, u) not in seen:
                edges.append((u, v, w))
                seen.add((u, v))

    dist = {n: float("inf") for n in graph}
    dist[start] = 0
    parent = {}

    # Relax edges V-1 times
    for _ in range(len(graph) - 1):
        changed = False
        for u, v, w in edges:
            # Try both directions (undirected graph)
            for a, b in [(u, v), (v, u)]:
                if dist[a] != float("inf") and dist[a] + w < dist[b]:
                    dist[b] = dist[a] + w
                    parent[b] = a
                    changed = True
        if not changed:
            break

    if dist[goal] == float("inf"):
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {
            "nodes": path,
            "distance": dist[goal],
            "algorithm": "Bellman-Ford",
        },
    }
