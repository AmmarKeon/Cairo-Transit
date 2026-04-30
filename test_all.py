import urllib.request
import json

print("Testing all endpoints...")

# Test 1
try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/nodes")
    data = json.loads(req.read().decode())
    print("[PASS] GET /api/network/nodes - " + str(len(data)) + " nodes")
except Exception as e:
    print("[FAIL] /api/network/nodes - " + str(e))

# Test 2
try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/mst")
    data = json.loads(req.read().decode())
    edges = data.get('data', {}).get('edges', [])
    print("[PASS] GET /api/network/mst - " + str(len(edges)) + " edges")
except Exception as e:
    print("[FAIL] /api/network/mst - " + str(e))

# Test 3
try:
    body = json.dumps({"start": "ramses", "goal": "57357"}).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:8000/api/route/emergency",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        path = data.get('data', {}).get('path', [])
        print("[PASS] POST /api/route/emergency - " + str(len(path)) + " stops")
except Exception as e:
    print("[FAIL] /api/route/emergency - " + str(e))

print("\nServer running at http://localhost:8000")