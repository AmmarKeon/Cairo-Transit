"""Test all API endpoints - requires backend running on localhost:8000"""
import urllib.request
import json

print("Testing all endpoints...")

# Test 1 - Nodes
try:
    req = urllib.request.urlopen("http://localhost:8000/api/nodes")
    data = json.loads(req.read().decode())
    print("[PASS] GET /api/nodes - " + str(len(data)) + " nodes")
except Exception as e:
    print("[FAIL] /api/nodes - " + str(e))

# Test 2 - Roads
try:
    req = urllib.request.urlopen("http://localhost:8000/api/roads")
    data = json.loads(req.read().decode())
    print("[PASS] GET /api/roads - " + str(len(data)) + " edges")
except Exception as e:
    print("[FAIL] /api/roads - " + str(e))

# Test 3 - MST
try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/mst")
    data = json.loads(req.read().decode())
    edges = data.get('data', {}).get('edges', [])
    print("[PASS] GET /api/network/mst - " + str(len(edges)) + " edges")
except Exception as e:
    print("[FAIL] /api/network/mst - " + str(e))

# Test 4 - Dijkstra route
try:
    req = urllib.request.urlopen("http://localhost:8000/api/route/dijkstra?start=ramses&goal=57357")
    data = json.loads(req.read().decode())
    path = data.get('data', {}).get('path', [])
    print("[PASS] GET /api/route/dijkstra - " + str(len(path)) + " coords")
except Exception as e:
    print("[FAIL] /api/route/dijkstra - " + str(e))

print("\nDone. Server should be running at http://localhost:8000")
