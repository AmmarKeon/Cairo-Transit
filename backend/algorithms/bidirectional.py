"""
Bidirectional Dijkstra - Searches from both start and goal simultaneously.
Meets in the middle, potentially exploring fewer nodes than standard Dijkstra.
Same optimal distance but different exploration pattern.
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

    if start == goal:
        return {
            "success": True,
            "data": {"nodes": [start], "distance": 0, "algorithm": "Bidirectional Dijkstra"},
        }

    # Forward search from start
    dist_f = {n: float("inf") for n in graph}
    dist_f[start] = 0
    parent_f = {}
    pq_f = [(0, start)]
    visited_f = set()

    # Backward search from goal
    dist_b = {n: float("inf") for n in graph}
    dist_b[goal] = 0
    parent_b = {}
    pq_b = [(0, goal)]
    visited_b = set()

    best_dist = float("inf")
    meeting = None

    while pq_f or pq_b:
        # Expand forward
        if pq_f:
            d, u = heapq.heappop(pq_f)
            if u in visited_f:
                continue
            visited_f.add(u)

            if u in visited_b:
                total = dist_f[u] + dist_b[u]
                if total < best_dist:
                    best_dist = total
                    meeting = u

            for v, w in graph.get(u, []):
                nd = dist_f[u] + w
                if nd < dist_f[v]:
                    dist_f[v] = nd
                    parent_f[v] = u
                    heapq.heappush(pq_f, (nd, v))

        # Expand backward
        if pq_b:
            d, u = heapq.heappop(pq_b)
            if u in visited_b:
                continue
            visited_b.add(u)

            if u in visited_f:
                total = dist_f[u] + dist_b[u]
                if total < best_dist:
                    best_dist = total
                    meeting = u

            for v, w in graph.get(u, []):
                nd = dist_b[u] + w
                if nd < dist_b[v]:
                    dist_b[v] = nd
                    parent_b[v] = u
                    heapq.heappush(pq_b, (nd, v))

        # Early termination
        if meeting:
            f_min = pq_f[0][0] if pq_f else float("inf")
            b_min = pq_b[0][0] if pq_b else float("inf")
            if f_min + b_min >= best_dist:
                break

    if meeting is None:
        return {"success": False, "error": "No path found"}

    # Build forward path: start -> meeting
    path_f = []
    n = meeting
    while n != start:
        path_f.append(n)
        n = parent_f[n]
    path_f.append(start)
    path_f.reverse()

    # Build backward path: meeting -> goal
    path_b = []
    n = meeting
    while n != goal:
        n = parent_b[n]
        path_b.append(n)

    full_path = path_f + path_b
    return {
        "success": True,
        "data": {
            "nodes": full_path,
            "distance": best_dist,
            "algorithm": "Bidirectional Dijkstra",
        },
    }
