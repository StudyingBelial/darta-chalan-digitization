#!/usr/bin/env bash
set -e

# Resolve repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Locate python3 or python
if command -v python3 >/dev/null 2>&1; then
    BASE_PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    BASE_PYTHON=python
else
    echo "[ERROR] Python 3 is required but not installed." >&2
    exit 1
fi

# Create virtual environment if it does not exist
if [ ! -f "venv/bin/activate" ] && [ ! -f ".venv/bin/activate" ]; then
    echo "[SETUP] Creating Python virtual environment: venv..."
    "$BASE_PYTHON" -m venv venv
    echo "[SUCCESS] Virtual environment created."
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Ensure requirements are installed
if ! python -c "import fastapi, uvicorn, sqlalchemy, pydantic, alembic" >/dev/null 2>&1; then
    echo "[SETUP] Installing Python dependencies from requirements.txt..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    echo "[SUCCESS] Python dependencies installed successfully."
fi

exec python run_app.py "$@"
