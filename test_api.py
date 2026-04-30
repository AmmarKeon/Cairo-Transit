import subprocess
import sys
import time
import traceback

# Start backend
print("Starting backend...")
proc = subprocess.Popen([sys.executable, "main.py"], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(4)

# Test
import urllib.request
try:
    req = urllib.request.urlopen("http://localhost:8000/api/nodes")
    content = req.read().decode()
    print("Nodes loaded:", len(content), "chars")
except Exception as e:
    print("Nodes error:", e)
    traceback.print_exc()

try:
    import json
    body = json.dumps({"start": "F2", "goal": "F9"}).encode()
    req = urllib.request.Request("http://localhost:8000/api/route", data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        print("Route:", result.get('success'))
except Exception as e:
    print("Route error:", e)
    traceback.print_exc()

proc.terminate()
print("Done")