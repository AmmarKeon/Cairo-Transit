"""GET /api/route/osrm (Valhalla real road geometry)"""
from backend.shared import NODES
from backend.road_geometry import get_road_path

def handler(request):
    start = request.args.get("start", "")
    goal = request.args.get("goal", "")
    if not start or not goal:
        return {"success": False, "error": "start and goal query params required"}
    if start not in NODES or goal not in NODES:
        return {"success": False, "error": "Invalid nodes"}

    path = get_road_path([start, goal], NODES)
    return {
        "success": True,
        "data": {
            "path": path,
            "nodes": [start, goal],
            "from": start,
            "to": goal,
            "algorithm": "Valhalla (OSM)"
        }
    }
