"""
Graph utilities - shared helpers for all algorithms.
"""
from typing import Dict, List, Tuple
import math


def reconstruct_path(parent: Dict[str, str], start: str, goal: str) -> List[str]:
    """Reconstruct path from parent dict. Returns [start, ..., goal]."""
    path = [goal]
    while path[-1] != start:
        prev = parent.get(path[-1])
        if prev is None:
            return []  # No path
        path.append(prev)
    return path[::-1]


def calculate_distance(path: List[str], graph: Dict[str, List[Tuple[str, float]]]) -> float:
    """Calculate total edge-weight distance along a path."""
    total = 0.0
    for i in range(len(path) - 1):
        for v, w in graph.get(path[i], []):
            if v == path[i + 1]:
                total += w
                break
    return total


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance in km between two lat/lng points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def heuristic(node_id: str, goal_id: str, nodes: Dict[str, dict]) -> float:
    """Euclidean heuristic in km for A*/Greedy. Returns 0 if nodes missing."""
    a = nodes.get(node_id)
    b = nodes.get(goal_id)
    if not a or not b:
        return 0.0
    return haversine_km(a["lat"], a["lng"], b["lat"], b["lng"])


def validate_nodes(start: str, goal: str, graph: Dict) -> str | None:
    """Return error string if nodes invalid, else None."""
    if start not in graph:
        return f"Start node '{start}' not in graph"
    if goal not in graph:
        return f"Goal node '{goal}' not in graph"
    return None
