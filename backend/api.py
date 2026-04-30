"""
Cairo Transit API - Vercel Python Serverless
Main entry point for all API routes.
Each endpoint function is exposed via URL path mapping.
"""
import json
import math
import os
import csv
import heapq
import random
import time
import urllib.request
import urllib.error
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

NODES = {**load_nodes(str(DATA_DIR / "neighborhoods.csv")), **load_nodes(str(DATA_DIR / "facilities.csv"))}
ROADS = load_roads(NODES)

GRAPH: Dict[str, List[Tuple[str, float]]] = {}
for a, b, dist in ROADS:
    if a not in GRAPH: GRAPH[a] = []
    if b not in GRAPH: GRAPH[b] = []
    GRAPH[a].append((b, dist))
    GRAPH[b].append((a, dist))

# ─── Graph Utilities ───────────────────────────────────────────────────────────

def reconstruct_path(parent: Dict[str, str], start: str, goal: str) -> List[str]:
    path = [goal]
    while path[-1] != start:
        prev = parent.get(path[-1])
        if prev is None:
            return []
        path.append(prev)
    return path[::-1]

def calculate_distance(path: List[str]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        for v, w in GRAPH.get(path[i], []):
            if v == path[i + 1]:
                total += w
                break
    return total

def haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def heuristic(node_id: str, goal_id: str) -> float:
    a = NODES.get(node_id)
    b = NODES.get(goal_id)
    if not a or not b:
        return 0.0
    return haversine(a["lat"], a["lng"], b["lat"], b["lng"])

# ─── Algorithms ───────────────────────────────────────────────────────────────

def dijkstra_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

    dist = {n: float("inf") for n in GRAPH}
    dist[start] = 0
    parent = {start: None}
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
    return {"success": True, "data": {"nodes": path, "distance": dist[goal], "algorithm": "Dijkstra"}}

def astar_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

    g_score = {n: float("inf") for n in GRAPH}
    g_score[start] = 0
    parent = {start: None}
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
    return {"success": True, "data": {"nodes": path, "distance": g_score[goal], "algorithm": "A*"}}

def bfs_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

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
    return {"success": True, "data": {"nodes": path, "distance": calculate_distance(path), "algorithm": "BFS"}}

def dfs_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

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
    return {"success": True, "data": {"nodes": path, "distance": calculate_distance(path), "algorithm": "DFS"}}

def greedy_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

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
    return {"success": True, "data": {"nodes": path, "distance": calculate_distance(path), "algorithm": "Greedy"}}

def bellmanford_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

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
    return {"success": True, "data": {"nodes": path, "distance": dist[goal], "algorithm": "Bellman-Ford"}}

def bidirectional_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}
    if start == goal: return {"success": True, "data": {"nodes": [start], "distance": 0, "algorithm": "Bidirectional"}}

    forward_parent = {start: None}
    backward_parent = {goal: None}
    forward_queue = [(0, start)]
    backward_queue = [(0, goal)]
    forward_dist = {start: 0}
    backward_dist = {goal: 0}
    meeting = None

    while forward_queue and backward_queue:
        d_u, u = heapq.heappop(forward_queue)
        if d_u > forward_dist.get(u, float("inf")):
            continue
        if u in backward_parent:
            meeting = u
            break
        for v, w in GRAPH.get(u, []):
            nd = forward_dist[u] + w
            if v not in forward_dist or nd < forward_dist[v]:
                forward_dist[v] = nd
                forward_parent[v] = u
                heapq.heappush(forward_queue, (nd, v))

        d_v, v = heapq.heappop(backward_queue)
        if d_v > backward_dist.get(v, float("inf")):
            continue
        if v in forward_parent:
            meeting = v
            break
        for u2, w in GRAPH.get(v, []):
            nd = backward_dist[v] + w
            if u2 not in backward_dist or nd < backward_dist[u2]:
                backward_dist[u2] = nd
                backward_parent[u2] = v
                heapq.heappush(backward_queue, (nd, u2))

    if meeting is None:
        return {"success": False, "error": "No path found"}

    forward_path = []
    node = meeting
    while node is not None:
        forward_path.append(node)
        node = forward_parent.get(node)
    forward_path.reverse()

    backward_path = []
    node = backward_parent.get(meeting)
    while node is not None:
        backward_path.append(node)
        node = backward_parent.get(node)

    path = forward_path + backward_path
    total_dist = forward_dist.get(meeting, float("inf")) + backward_dist.get(meeting, 0)
    return {"success": True, "data": {"nodes": path, "distance": total_dist, "algorithm": "Bidirectional"}}

def randomwalk_algo(start: str, goal: str) -> dict:
    if start not in GRAPH: return {"success": False, "error": f"Start '{start}' not found"}
    if goal not in GRAPH: return {"success": False, "error": f"Goal '{goal}' not found"}

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
            weights = [max(1.0 / (heuristic(v, goal) + 0.1), 0.1) for v, w in neighbors]
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
            dist = calculate_distance(path)
            if dist < best_dist:
                best_dist = dist
                best_path = path

    if not best_path:
        return {"success": False, "error": "No path found after 30 attempts"}

    return {"success": True, "data": {"nodes": best_path, "distance": best_dist, "algorithm": "Random Walk"}}

def mst_algo() -> dict:
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

    return {"success": True, "data": {"edges": mst_edges, "total_weight": total_weight, "node_count": len(GRAPH)}}

# ─── Road Geometry ────────────────────────────────────────────────────────────

_GEOMETRY_CACHE: Dict[str, List[List[float]]] = {}

def _decode_polyline6(encoded: str) -> List[List[float]]:
    coords = []
    index = 0
    lat = lng = 0
    while index < len(encoded):
        shift = result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat
        shift = result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng
        coords.append([lat / 1e6, lng / 1e6])
    return coords

def _get_segment_coords(from_lng: float, from_lat: float, to_lng: float, to_lat: float) -> Optional[List[List[float]]]:
    key = f"{round(from_lng,6)},{round(from_lat,6)};{round(to_lng,6)},{round(to_lat,6)}"
    if key in _GEOMETRY_CACHE:
        return _GEOMETRY_CACHE[key]

    time.sleep(0.1)  # Rate limit

    payload = json.dumps({
        "locations": [{"lat": from_lat, "lon": from_lng}, {"lat": to_lat, "lon": to_lng}],
        "costing": "auto", "directions_options": {"units": "kilometers"}
    }).encode()

    try:
        req = urllib.request.Request(
            "https://valhalla1.openstreetmap.de/route",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "CairoTransit/7.0.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        legs = data.get("trip", {}).get("legs", [])
        if legs and legs[0].get("shape"):
            coords = _decode_polyline6(legs[0]["shape"])
            _GEOMETRY_CACHE[key] = coords
            return coords
    except Exception:
        pass
    return None

def get_road_path(node_path: List[str]) -> List[List[float]]:
    if len(node_path) < 2:
        return []
    full_path = []
    for i in range(len(node_path) - 1):
        from_node = NODES.get(node_path[i])
        to_node = NODES.get(node_path[i + 1])
        if not from_node or not to_node:
            continue
        segment = _get_segment_coords(from_node['lng'], from_node['lat'], to_node['lng'], to_node['lat'])
        if segment:
            if full_path and segment and full_path[-1] == segment[0]:
                segment = segment[1:]
            full_path.extend(segment)
        else:
            if not full_path or full_path[-1] != [from_node['lat'], from_node['lng']]:
                full_path.append([from_node['lat'], from_node['lng']])
            full_path.append([to_node['lat'], to_node['lng']])
    return full_path

# ─── Algorithm Registry ────────────────────────────────────────────────────────

ALGOS = {
    "dijkstra": dijkstra_algo,
    "astar": astar_algo,
    "bfs": bfs_algo,
    "dfs": dfs_algo,
    "greedy": greedy_algo,
    "bellmanford": bellmanford_algo,
    "bidirectional": bidirectional_algo,
    "randomwalk": randomwalk_algo,
}

# ─── Vercel Handler ──────────────────────────────────────────────────────────

def handler(request):
    path = request.path
    qs = request.args

    # GET /api/nodes
    if path == "/api/nodes":
        return [NODES[n] for n in sorted(NODES.keys())]

    # GET /api/algorithms
    if path == "/api/algorithms":
        return [
            {"key": "dijkstra", "name": "Dijkstra's Algorithm", "complexity": "O((V+E) log V)", "color": "#22c55e", "implemented": True},
            {"key": "astar", "name": "A* Search", "complexity": "O((V+E) log V)", "color": "#8b5cf6", "implemented": True},
            {"key": "bfs", "name": "Breadth-First Search", "complexity": "O(V+E)", "color": "#eab308", "implemented": True},
            {"key": "dfs", "name": "Depth-First Search", "complexity": "O(V+E)", "color": "#0ea5e9", "implemented": True},
            {"key": "greedy", "name": "Greedy Best-First", "complexity": "O((V+E) log V)", "color": "#f43f5e", "implemented": True},
            {"key": "bellmanford", "name": "Bellman-Ford", "complexity": "O(V*E)", "color": "#14b8a6", "implemented": True},
            {"key": "bidirectional", "name": "Bidirectional Dijkstra", "complexity": "O((V+E) log V)", "color": "#ec4899", "implemented": True},
            {"key": "randomwalk", "name": "Random Walk", "complexity": "O(n)", "color": "#a855f7", "implemented": True},
            {"key": "osrm", "name": "Valhalla (OSM)", "complexity": "Real-world", "color": "#3b82f6", "implemented": True},
            {"key": "mst", "name": "Minimum Spanning Tree", "complexity": "O(E log E)", "color": "#1a3a3a", "implemented": True},
        ]

    # GET /api/network/mst
    if path == "/api/network/mst":
        return mst_algo()

    # GET /api/route/<algo>
    if path.startswith("/api/route/"):
        algo = path.split("/")[-1]
        start = qs.get("start", "")
        goal = qs.get("goal", "")
        if not start or not goal:
            return {"success": False, "error": "start and goal query params required"}

        if algo == "osrm":
            coords = get_road_path([start, goal])
            return {"success": True, "data": {"path": coords, "nodes": [start, goal], "from": start, "to": goal, "algorithm": "Valhalla (OSM)"}}

        algo_fn = ALGOS.get(algo)
        if not algo_fn:
            return {"success": False, "error": f"Unknown algorithm: {algo}"}

        result = algo_fn(start, goal)
        if result.get("success") and "data" in result:
            node_ids = result["data"].get("nodes", [])
            result["data"]["path"] = get_road_path(node_ids)
            result["data"]["from"] = start
            result["data"]["to"] = goal
        return result

    # GET / or unknown
    if path in ("/", ""):
        return {
            "message": "Cairo Transit API",
            "endpoints": ["/api/nodes", "/api/route/<algo>", "/api/network/mst", "/api/algorithms"]
        }

    return {"success": False, "error": "Not found"}, 404
