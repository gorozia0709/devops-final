import urllib.request
import datetime
import sys

PORTS = [5000, 5001]


def check():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    any_ok = False
    for port in PORTS:
        url = f"http://localhost:{port}/health"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    print(f"[{timestamp}] OK - {url} returned 200")
                    any_ok = True
        except Exception:
            print(f"[{timestamp}] FAIL - {url} unreachable")

    if not any_ok:
        print(f"[{timestamp}] CRITICAL - no slots responding")
        sys.exit(1)


if __name__ == "__main__":
    check()
