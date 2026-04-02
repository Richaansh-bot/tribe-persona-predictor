import subprocess
import sys
import os
import time

# Change to the project directory
os.chdir(r"C:\Users\giris\persona-predictor")

# Kill any existing process on port 8003
try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue",
        ],
        capture_output=True,
        text=True,
    )
    time.sleep(1)
except:
    pass

# Start the server
proc = subprocess.Popen(
    [
        r"C:\Users\giris\persona-predictor\tribev2_env\Scripts\python.exe",
        "-m",
        "uvicorn",
        "server:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8003",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

print(f"Started server with PID: {proc.pid}")
print("Waiting for server to start...")

time.sleep(5)

# Check if still running
if proc.poll() is None:
    print("Server is running!")
else:
    stdout, stderr = proc.communicate()
    print(f"Server exited with code: {proc.returncode}")
    print(f"stdout: {stdout.decode()}")
    print(f"stderr: {stderr.decode()}")
