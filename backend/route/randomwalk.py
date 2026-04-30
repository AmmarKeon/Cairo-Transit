"""GET /api/route/randomwalk"""
from backend.shared import randomwalk, NODES
from backend.road_geometry import get_road_path

def handler(request):
    start = request.args.get("start", "")
    goal = request.args.get("goal", "")
    if not start or not goal:
        return {"success": False, "error": "start and goal query params required"}
    result = randomwalk(start, goal)
    if result.get("success") and "data" in result:
        result["data"]["path"] = get_road_path(result["data"].get("nodes", []), NODES)
        result["data"]["from"] = start
        result["data"]["to"] = goal
    return result
