import subprocess
import sys
import os

os.chdir("backend")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

import time
time.sleep(3)

print(f"Server started with PID: {proc.pid}")
print("Testing endpoints...")

import urllib.request
import json

try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/nodes")
    data = json.loads(req.read().decode())
    print(f"Nodes API: {len(data)} nodes")
except Exception as e:
    print(f"Error: {e}")

try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/mst")
    data = json.loads(req.read().decode())
    print(f"MST API: {len(data.get('data', {}).get('edges', []))} edges")
except Exception as e:
    print(f"Error: {e}")

print("\nServer running at http://localhost:8000")
print("Press Enter to stop server...")

input()
proc.terminate()
print("Server stopped")