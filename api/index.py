"""Vercel Python API entry point - routes to sub-handlers."""
from api.shared import (
    dijkstra, astar, bfs, dfs, greedy,
    bellmanford, bidirectional, randomwalk, mst, NODES
)
from api.road_geometry import get_road_path

def handler(request):
    path = request.path
    qs = request.args

    # Route: /api/nodes
    if path == "/api/nodes":
        return [NODES[n] for n in sorted(NODES.keys())]

    # Route: /api/algorithms
    if path == "/api/algorithms":
        from api.algorithms import handler as alg_handler
        return alg_handler(request)

    # Route: /api/network/mst
    if path == "/api/network/mst":
        return mst()

    # Route: /api/route/<algo>
    if path.startswith("/api/route/"):
        algo = path.split("/")[-1]
        start = qs.get("start", "")
        goal = qs.get("goal", "")
        if not start or not goal:
            return {"success": False, "error": "start and goal required"}

        algo_map = {
            "dijkstra": dijkstra,
            "astar": astar,
            "bfs": bfs,
            "dfs": dfs,
            "greedy": greedy,
            "bellmanford": bellmanford,
            "bidirectional": bidirectional,
            "randomwalk": randomwalk,
            "osrm": None,
        }

        if algo == "osrm":
            path_coords = get_road_path([start, goal], NODES)
            return {"success": True, "data": {"path": path_coords, "nodes": [start, goal], "from": start, "to": goal, "algorithm": "Valhalla (OSM)"}}

        algo_fn = algo_map.get(algo)
        if not algo_fn:
            return {"success": False, "error": f"Unknown algorithm: {algo}"}

        result = algo_fn(start, goal)
        if result.get("success") and "data" in result:
            node_ids = result["data"].get("nodes", [])
            result["data"]["path"] = get_road_path(node_ids, NODES)
            result["data"]["from"] = start
            result["data"]["to"] = goal
        return result

    # Route: /
    if path in ("/", ""):
        return {
            "message": "Cairo Transit API",
            "endpoints": ["/api/nodes", "/api/route/<algo>", "/api/network/mst", "/api/algorithms"]
        }

    return {"success": False, "error": "Not found"}, 404
