"""Start backend server and test endpoints.
Run from project root: python scripts/run_server.py"""
import subprocess
import sys
import os
import time

project_root = os.path.join(os.path.dirname(__file__), '..')
backend_dir = os.path.join(project_root, 'backend')

os.chdir(backend_dir)
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

time.sleep(3)

print(f"Server started with PID: {proc.pid}")
print("Testing endpoints...")

import urllib.request
import json

try:
    req = urllib.request.urlopen("http://localhost:8000/api/nodes")
    data = json.loads(req.read().decode())
    print(f"[PASS] Nodes API: {len(data)} nodes")
except Exception as e:
    print(f"[FAIL] Nodes API: {e}")

try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/mst")
    data = json.loads(req.read().decode())
    print(f"[PASS] MST API: {len(data.get('data', {}).get('edges', []))} edges")
except Exception as e:
    print(f"[FAIL] MST API: {e}")

print("\nServer running at http://localhost:8000")
print("Press Enter to stop server...")

input()
proc.terminate()
print("Server stopped")
