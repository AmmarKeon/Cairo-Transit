"""
Shared graph data and algorithm implementations.
Loaded at module level so it persists across function invocations in the same instance.
"""
import csv
import math
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ─── Data Loading ───────────────────────────────────────────────────────────────

DATA_DIR = Path(os.path.dirname(__file__)).parent / "data"

def load_nodes(filepath: str) -> Dict[str, dict]:
    nodes = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'ID' not in row or 'Name' not in row:
                continue
            node_id = row['ID']
            if node_id in nodes:
                continue
            nodes[node_id] = {
                "id": node_id,
                "name": row['Name'],
                "lat": float(row['Y-coordinate']),
                "lng": float(row['X-coordinate']),
                "type": row.get('Type', 'Unknown'),
            }
    return nodes

def load_roads(nodes: Dict[str, dict]) -> List[Tuple[str, str, float]]:
    roads = []
    with open(DATA_DIR / "existing_roads.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_id = row['FromID']
            to_id = row['ToID']
            distance = float(row['Distance(km)'])
            if from_id not in nodes or to_id not in nodes:
                continue
            roads.append((from_id, to_id, distance))
    return roads

# Load data once at module import
NODES = {**load_nodes(str(DATA_DIR / "neighborhoods.csv")), **load_nodes(str(DATA_DIR / "facilities.csv"))}
ROADS = load_roads(NODES)

# Build graph
GRAPH: Dict[str, List[Tuple[str, float]]] = {}
for a, b, dist in ROADS:
    if a not in GRAPH: GRAPH[a] = []
    if b not in GRAPH: GRAPH[b] = []
    GRAPH[a].append((b, dist))
    GRAPH[b].append((a, dist))

# ─── Graph Utilities ─────────────────────────────────────────────────────────────

def reconstruct_path(parent: Dict[str, str], start: str, goal: str) -> List[str]:
    path = [goal]
    while path[-1] != start:
        prev = parent.get(path[-1])
        if prev is None:
            return []
        path.append(prev)
    return path[::-1]

def calculate_distance(path: List[str], graph: Dict[str, List[Tuple[str, float]]]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        for v, w in graph.get(path[i], []):
            if v == path[i + 1]:
                total += w
                break
    return total

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def heuristic(node_id: str, goal_id: str) -> float:
    a = NODES.get(node_id)
    b = NODES.get(goal_id)
    if not a or not b:
        return 0.0
    return haversine_km(a["lat"], a["lng"], b["lat"], b["lng"])

def validate_nodes(start: str, goal: str) -> Optional[str]:
    if start not in GRAPH:
        return f"Start node '{start}' not in graph"
    if goal not in GRAPH:
        return f"Goal node '{goal}' not in graph"
    return None

# ─── Algorithm Implementations ───────────────────────────────────────────────────

import heapq

def dijkstra(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    dist = {n: float("inf") for n in GRAPH}
    dist[start] = 0
    parent = {}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == goal:
            break
        for v, w in GRAPH.get(u, []):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    if dist[goal] == float("inf"):
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {"nodes": path, "distance": dist[goal], "algorithm": "Dijkstra"}
    }

def astar(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    g_score = {n: float("inf") for n in GRAPH}
    g_score[start] = 0
    parent = {}
    f_score = {n: float("inf") for n in GRAPH}
    f_score[start] = heuristic(start, goal)
    open_set = [(f_score[start], start)]

    while open_set:
        _, u = heapq.heappop(open_set)
        if u == goal:
            break
        for v, w in GRAPH.get(u, []):
            tentative_g = g_score[u] + w
            if tentative_g < g_score[v]:
                parent[v] = u
                g_score[v] = tentative_g
                f_score[v] = tentative_g + heuristic(v, goal)
                heapq.heappush(open_set, (f_score[v], v))

    if g_score[goal] == float("inf"):
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {"nodes": path, "distance": g_score[goal], "algorithm": "A*"}
    }

def bfs(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    parent = {start: None}
    queue = [start]

    while queue:
        u = queue.pop(0)
        if u == goal:
            break
        for v, _ in GRAPH.get(u, []):
            if v not in parent:
                parent[v] = u
                queue.append(v)

    if goal not in parent:
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {"nodes": path, "distance": calculate_distance(path, GRAPH), "algorithm": "BFS"}
    }

def dfs(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    parent = {start: None}
    stack = [start]

    while stack:
        u = stack.pop()
        if u == goal:
            break
        for v, _ in GRAPH.get(u, []):
            if v not in parent:
                parent[v] = u
                stack.append(v)

    if goal not in parent:
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {"nodes": path, "distance": calculate_distance(path, GRAPH), "algorithm": "DFS"}
    }

def greedy(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    parent = {start: None}
    pq = [(heuristic(start, goal), start)]

    while pq:
        _, u = heapq.heappop(pq)
        if u == goal:
            break
        for v, w in GRAPH.get(u, []):
            if v not in parent:
                parent[v] = u
                heapq.heappush(pq, (heuristic(v, goal), v))

    if goal not in parent:
        return {"success": False, "error": "No path found"}

    path = reconstruct_path(parent, start, goal)
    return {
        "success": True,
        "data": {"nodes": path, "distance": calculate_distance(path, GRAPH), "algorithm": "Greedy"}
    }

def bellmanford(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    edges = []
    seen = set()
    for u, neighbors in GRAPH.items():
        for v, w in neighbors:
            if (u, v) not in seen and (v, u) not in seen:
                edges.append((u, v, w))
                seen.add((u, v))

    dist = {n: float("inf") for n in GRAPH}
    dist[start] = 0
    parent = {}

    for _ in range(len(GRAPH) - 1):
        changed = False
        for u, v, w in edges:
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
        "data": {"nodes": path, "distance": dist[goal], "algorithm": "Bellman-Ford"}
    }

def bidirectional(start: str, goal: str) -> dict:
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    if start == goal:
        return {"success": True, "data": {"nodes": [start], "distance": 0, "algorithm": "Bidirectional"}}

    forward_parent = {start: None}
    backward_parent = {goal: None}
    forward_queue = [(0, start)]
    backward_queue = [(0, goal)]
    forward_dist = {start: 0}
    backward_dist = {goal: 0}
    meeting_node = None

    while forward_queue and backward_queue:
        # Forward search
        d_u, u = heapq.heappop(forward_queue)
        if d_u > forward_dist.get(u, float("inf")):
            continue
        if u in backward_parent:
            meeting_node = u
            break
        for v, w in GRAPH.get(u, []):
            new_dist = forward_dist[u] + w
            if v not in forward_dist or new_dist < forward_dist[v]:
                forward_dist[v] = new_dist
                forward_parent[v] = u
                heapq.heappush(forward_queue, (new_dist, v))

        # Backward search
        d_v, v = heapq.heappop(backward_queue)
        if d_v > backward_dist.get(v, float("inf")):
            continue
        if v in forward_parent:
            meeting_node = v
            break
        for u2, w in GRAPH.get(v, []):
            new_dist = backward_dist[v] + w
            if u2 not in backward_dist or new_dist < backward_dist[u2]:
                backward_dist[u2] = new_dist
                backward_parent[u2] = v
                heapq.heappush(backward_queue, (new_dist, u2))

    if meeting_node is None:
        return {"success": False, "error": "No path found"}

    # Reconstruct forward path
    forward_path = []
    node = meeting_node
    while node is not None:
        forward_path.append(node)
        node = forward_parent.get(node)
    forward_path.reverse()

    # Reconstruct backward path
    backward_path = []
    node = backward_parent.get(meeting_node)
    while node is not None:
        backward_path.append(node)
        node = backward_parent.get(node)

    path = forward_path + backward_path
    total_dist = forward_dist.get(meeting_node, float("inf")) + backward_dist.get(meeting_node, 0)

    return {
        "success": True,
        "data": {"nodes": path, "distance": total_dist, "algorithm": "Bidirectional"}
    }

def randomwalk(start: str, goal: str) -> dict:
    import random
    err = validate_nodes(start, goal)
    if err:
        return {"success": False, "error": err}

    best_path = []
    best_dist = float("inf")

    for _ in range(30):
        current = start
        path = [current]
        visited = {start}
        attempts = 0

        while current != goal and attempts < 100:
            neighbors = GRAPH.get(current, [])
            if not neighbors:
                break
            # Bias toward goal
            weights = []
            for v, w in neighbors:
                h = heuristic(v, goal)
                weights.append(max(1.0 / (h + 0.1), 0.1))
            total_w = sum(weights)
            r = random.random() * total_w
            cumsum = 0
            next_node = neighbors[-1][0]
            for i, (v, w) in enumerate(neighbors):
                cumsum += weights[i]
                if cumsum >= r:
                    next_node = v
                    break

            if next_node in visited:
                break
            current = next_node
            path.append(current)
            visited.add(current)
            attempts += 1

        if current == goal:
            dist = calculate_distance(path, GRAPH)
            if dist < best_dist:
                best_dist = dist
                best_path = path

    if not best_path:
        return {"success": False, "error": "No path found after 30 attempts"}

    return {
        "success": True,
        "data": {"nodes": best_path, "distance": best_dist, "algorithm": "Random Walk"}
    }

def mst() -> dict:
    """Kruskal's MST - returns edges connecting all nodes."""
    edges = []
    seen = set()
    for u, neighbors in GRAPH.items():
        for v, w in neighbors:
            if (u, v) not in seen and (v, u) not in seen:
                edges.append((w, u, v))
                seen.add((u, v))

    edges.sort()
    parent = {n: n for n in GRAPH}
    rank = {n: 0 for n in GRAPH}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    mst_edges = []
    total_weight = 0.0

    for w, u, v in edges:
        if union(u, v):
            mst_edges.append({"from": NODES[u], "to": NODES[v], "weight": w})
            total_weight += w
        if len(mst_edges) == len(GRAPH) - 1:
            break

    return {
        "success": True,
        "data": {
            "edges": mst_edges,
            "total_weight": total_weight,
            "node_count": len(GRAPH),
        }
    }
