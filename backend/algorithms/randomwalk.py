"""
Random Walk - Randomly picks next neighbors with slight goal bias.
Produces chaotic, inefficient paths. Shows why we need proper algorithms.
Runs multiple attempts and picks the LONGEST valid path.
"""
import random
from typing import Dict, List, Tuple
from .graph import calculate_distance, heuristic, validate_nodes


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
            "data": {"nodes": [start], "distance": 0, "algorithm": "Random Walk"},
        }

    best_path = None
    best_dist = 0

    for _ in range(30):  # 30 attempts
        current = start
        path = [current]
        visited = {current}

        for _ in range(25):  # max 25 steps
            if current == goal:
                break
            neighbors = [(v, w) for v, w in graph.get(current, []) if v not in visited]
            if not neighbors:
                break

            # Weight toward goal but add randomness
            weights = []
            for v, w in neighbors:
                h = heuristic(v, goal, nodes)
                # Prefer closer-to-goal but add heavy randomness
                weights.append(1.0 / (h + 0.1) + random.random() * 2.0)

            total = sum(weights)
            probs = [w / total for w in weights]
            chosen = random.choices(neighbors, weights=probs, k=1)[0]

            current = chosen[0]
            path.append(current)
            visited.add(current)

        if current == goal:
            dist = calculate_distance(path, graph)
            if dist > best_dist:
                best_dist = dist
                best_path = path

    if best_path is None:
        return {"success": False, "error": "Random walk failed to find path"}

    return {
        "success": True,
        "data": {
            "nodes": best_path,
            "distance": best_dist,
            "algorithm": "Random Walk",
        },
    }
