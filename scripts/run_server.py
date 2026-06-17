#!/usr/bin/env python3
"""
Start Uvicorn and print the URL only after GET /api/health returns 200.

Usage: python scripts/run_server.py <uvicorn-path>
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HEALTH_URL = "http://127.0.0.1:8000/api/health"
TIMEOUT_S  = 30
POLL_S     = 0.25


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: run_server.py <uvicorn-bin>", file=sys.stderr)
        sys.exit(1)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spa_dir   = os.path.join(repo_root, "frontend", "dist")

    uvicorn = sys.argv[1]
    env = os.environ.copy()
    env["HUENIFORM_SPA_DIR"] = spa_dir

    proc = subprocess.Popen(
        [uvicorn, "app.main:app",
         "--host", "127.0.0.1", "--port", "8000",
         "--log-level", "warning"],
        cwd=os.path.join(repo_root, "backend"),
        env=env,
    )

    deadline = time.monotonic() + TIMEOUT_S
    while True:
        if proc.poll() is not None:
            sys.exit(proc.returncode or 1)
        try:
            urllib.request.urlopen(HEALTH_URL, timeout=1)
            break
        except (urllib.error.URLError, OSError):
            if time.monotonic() >= deadline:
                proc.terminate()
                proc.wait()
                print("Timed out waiting for server to start.", file=sys.stderr)
                sys.exit(1)
            time.sleep(POLL_S)

    print("Hueniform → http://127.0.0.1:8000", flush=True)

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    main()
