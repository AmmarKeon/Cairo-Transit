"""Test API endpoints - starts backend, runs tests, then stops.
Run from project root: python scripts/test_api.py"""
import subprocess
import sys
import os
import time
import traceback

project_root = os.path.join(os.path.dirname(__file__), '..')

# Start backend
print("Starting backend...")
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    cwd=os.path.join(project_root, "backend"),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
time.sleep(4)

# Test
import urllib.request
import json

try:
    req = urllib.request.urlopen("http://localhost:8000/api/nodes")
    content = req.read().decode()
    data = json.loads(content)
    print(f"[PASS] Nodes loaded: {len(data)} nodes")
except Exception as e:
    print(f"[FAIL] Nodes error: {e}")
    traceback.print_exc()

try:
    req = urllib.request.urlopen("http://localhost:8000/api/route/dijkstra?start=F2&goal=F9")
    result = json.loads(req.read())
    print(f"[PASS] Dijkstra route: {result.get('success')}")
except Exception as e:
    print(f"[FAIL] Route error: {e}")
    traceback.print_exc()

proc.terminate()
proc.wait()
print("Done")
