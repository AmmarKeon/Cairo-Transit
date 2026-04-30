import subprocess
import sys
import os
import time

# Start backend
print("Starting backend server...")
backend_proc = subprocess.Popen(
    [sys.executable, "main.py"],
    cwd="backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
time.sleep(3)

# Test backend
import urllib.request
try:
    req = urllib.request.urlopen("http://localhost:8000/api/network/nodes")
    data = req.read().decode()
    print(f"Backend OK - nodes loaded")
except Exception as e:
    print(f"Backend error: {e}")
    backend_proc.terminate()
    sys.exit(1)

# Start frontend
print("Starting frontend server...")
frontend_proc = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd="frontend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("\n" + "="*50)
print("Servers running!")
print("Backend: http://localhost:8000")
print("Frontend: http://localhost:5173")
print("="*50)
print("\nPress Enter to stop servers...")

input()
frontend_proc.terminate()
backend_proc.terminate()
print("Servers stopped")