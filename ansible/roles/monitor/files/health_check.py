import urllib.request
import datetime
import subprocess
import sys

URL = "http://localhost:5000/health"


def check():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with urllib.request.urlopen(URL, timeout=5) as response:
            if response.status == 200:
                print(f"[{timestamp}] OK - app is healthy")
                return
    except Exception as e:
        print(f"[{timestamp}] FAIL - app unreachable: {e}")
        print(f"[{timestamp}] Attempting automatic restart...")
        result = subprocess.run(
            ["docker", "compose", "restart", "app"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[{timestamp}] Restart successful")
        else:
            print(f"[{timestamp}] Restart failed: {result.stderr}")
            sys.exit(1)


if __name__ == "__main__":
    check()