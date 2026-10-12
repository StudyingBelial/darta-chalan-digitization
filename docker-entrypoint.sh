#!/bin/bash
set -e

echo "============================================================================"
echo "  [NTC] Starting Darta-Chalan Digitization Backend (Docker)"
echo "============================================================================"

# Wait for PostgreSQL database to be ready
python3 - << 'EOF'
import os, time, sys
from sqlalchemy import create_engine

db_url = os.environ.get("DATABASE_URL", "")
if db_url and not db_url.startswith("sqlite"):
    print("[INIT] Waiting for PostgreSQL database connection...")
    for i in range(30):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                print("[INIT] Database connected successfully.")
                sys.exit(0)
        except Exception as e:
            time.sleep(1)
    print(f"[INIT ERROR] Failed to connect to database: {e}", file=sys.stderr)
    sys.exit(1)
EOF

echo "[INIT] Applying database migrations..."
if alembic upgrade head; then
    echo "[INIT] Alembic migrations applied successfully."
else
    echo "[INIT WARN] Alembic sync notice. Ensuring tables via SQLAlchemy models..."
    python3 -c "from backend.app.db.base import Base, engine; import backend.app.db.models; Base.metadata.create_all(bind=engine)"
fi

echo "[INIT] Checking and seeding initial master data & administrator..."
python3 -c "from backend.scripts.seed import seed_database; seed_database()"

echo "[INIT] Starting Uvicorn API server on 0.0.0.0:8000..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2
