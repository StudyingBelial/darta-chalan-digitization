#!/usr/bin/env bash
set -e

# Resolve repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Delegate to python3 run_app.py if python3 is available
if command -v python3 >/dev/null 2>&1; then
    exec python3 run_app.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python run_app.py "$@"
else
    # Fallback directly to docker compose
    echo "[INFO] Python not found. Running Docker Compose directly..."
    exec docker compose up --build "$@"
fi
