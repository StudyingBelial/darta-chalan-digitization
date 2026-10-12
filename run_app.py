#!/usr/bin/env python3
"""
=============================================================================
 Darta-Chalan Digitization System (दर्ता-चलानी डिजिटल प्रणाली)
 Universal Single-Command Application Host & Runner
=============================================================================
"""

import os
import sys
import shutil
import argparse
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
STORAGE_DIR = ROOT_DIR / "storage"

def print_banner(host: str, port: int, mode: str = "Production (Unified)"):
    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    smtp_port = os.getenv("SMTP_SCANNER_PORT", "1025")
    print("\n" + "=" * 76)
    print("  [NTC] NEPAL TELECOM CORPORATION")
    print("  Darta-Chalan Digitization System (दर्ता-चलानी डिजिटल प्रणाली)")
    print("=" * 76)
    print(f"  * Running Mode       : {mode}")
    print(f"  * Web Application   : http://{display_host}:{port}")
    print(f"  * REST API Docs      : http://{display_host}:{port}/docs")
    print(f"  * ReDoc Explorer     : http://{display_host}:{port}/redoc")
    print(f"  * System Health Check: http://{display_host}:{port}/health")
    print(f"  * SMTP Scanner Intake: smtp://{display_host}:{smtp_port} (Canon/MFP Scan-to-Email)")
    print("-" * 76)
    print("  Default System Administrator Credentials:")
    print("     * Email    : admin@ntc.net.np")
    print("     * Password : Admin@123456")
    print("     * Role     : SYSTEM_ADMIN")
    print("=" * 76)
    print("  Press Ctrl+C to stop the server safely.\n")

def check_and_setup_env():
    """Ensure .env exists; if not, create from .env.example."""
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("[SETUP] Creating .env configuration from .env.example...")
        shutil.copyfile(env_example, env_file)
        print("[SUCCESS] .env file initialized.")

def ensure_storage_directories():
    """Ensure required runtime storage directories exist."""
    dirs_to_create = [
        STORAGE_DIR / "logs",
        STORAGE_DIR / "uploads" / "darta",
        STORAGE_DIR / "uploads" / "chalan",
        STORAGE_DIR / "uploads" / "inbound",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
    # Ensure gitkeep files exist
    for keep_dir in [STORAGE_DIR / "logs", STORAGE_DIR / "uploads"]:
        keep_file = keep_dir / ".gitkeep"
        if not keep_file.exists():
            keep_file.touch()

def check_and_install_dependencies():
    """Verify that backend Python dependencies are installed."""
    critical_modules = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "jose", "jwt"]
    missing = False
    for mod in ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]:
        try:
            __import__(mod)
        except ImportError:
            missing = True
            break
    
    if missing:
        req_file = ROOT_DIR / "requirements.txt"
        if req_file.exists():
            print("[SETUP] Installing Python dependencies from requirements.txt...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
            print("[SUCCESS] Python dependencies installed.")

def ensure_database_and_seed(force_seed: bool = False):
    """Run database migrations and seed default data if DB is fresh."""
    print("[DB] Checking database state and schema migrations...")
    sys.path.insert(0, str(ROOT_DIR))
    
    try:
        from alembic.config import Config
        from alembic import command
        alembic_ini = ROOT_DIR / "alembic.ini"
        if alembic_ini.exists():
            alembic_cfg = Config(str(alembic_ini))
            command.upgrade(alembic_cfg, "head")
            print("[DB] Alembic database migrations up-to-date.")
    except Exception as e:
        print(f"[NOTE] Alembic migration notice: {e}. Ensuring tables via SQLAlchemy models...")

    # Ensure tables are created via SQLAlchemy metadata regardless
    try:
        from backend.app.db.base import Base, engine, SessionLocal
        import backend.app.db.models
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[NOTE] Schema initialization: {e}")

    # Check if seeding is needed
    try:
        from backend.app.db.base import SessionLocal
        from backend.app.db.models.users import Users
        with SessionLocal() as db:
            user_count = db.query(Users).count()
            if user_count == 0 or force_seed:
                print("[SEED] Database is empty or --seed specified. Seeding initial system data...")
                from backend.scripts.seed import seed_database
                seed_database()
                print("[SUCCESS] System seeded successfully.")
            else:
                print(f"[DB] Database verified ({user_count} registered users found).")
    except Exception as e:
        print(f"[WARN] Notice during database check/seed: {e}")

def get_npm_executable() -> str:
    """Resolve npm executable reliably across platforms."""
    if sys.platform == "win32":
        cmd = shutil.which("npm.cmd") or shutil.which("npm")
        return cmd if cmd else "npm.cmd"
    cmd = shutil.which("npm")
    return cmd if cmd else "npm"

def ensure_frontend_build(force_build: bool = False):
    """Verify frontend dependencies and compiled dist/ bundle."""
    node_modules = FRONTEND_DIR / "node_modules"
    npm_cmd = get_npm_executable()
    
    # 1. Ensure node_modules exist
    if not node_modules.exists():
        print("[SETUP] Frontend node_modules not detected. Installing npm dependencies...")
        try:
            subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), check=True, shell=(sys.platform == "win32"))
            print("[SUCCESS] Frontend npm dependencies installed.")
        except Exception as e:
            print(f"[WARN] npm install encountered issue: {e}")

    # 2. Ensure dist/index.html exists
    index_html = FRONTEND_DIST / "index.html"
    if not index_html.exists() or force_build:
        print("[BUILD] Frontend build not found or rebuild requested. Building React application...")
        try:
            subprocess.run([npm_cmd, "run", "build"], cwd=str(FRONTEND_DIR), check=True, shell=(sys.platform == "win32"))
            print("[SUCCESS] Frontend compiled successfully to frontend/dist/.")
        except FileNotFoundError:
            print("[WARN] 'npm' not found on system PATH. If you have NodeJS installed, please run 'npm run build' inside frontend/.")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Frontend build returned error: {e}. FastAPI will still serve API routes.")
    else:
        print("[SUCCESS] Frontend production bundle verified in frontend/dist.")

def run_dev_servers(host: str, port: int):
    """Run FastAPI backend and Vite frontend concurrently in development mode."""
    print("[DEV] Starting in Development Mode (Vite Dev Server + FastAPI)...")
    npm_cmd = get_npm_executable()
    
    # Start Vite in frontend/
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev"], cwd=str(FRONTEND_DIR), shell=(sys.platform == "win32"))
    
    print_banner(host, port, mode="Development Mode (Vite: http://localhost:3000 | FastAPI: http://localhost:8000)")
    
    try:
        import uvicorn
        uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)
    finally:
        frontend_proc.terminate()

def run_production_server(host: str, port: int, reload: bool, open_browser: bool):
    """Run unified FastAPI application serving REST APIs and React SPA."""
    ensure_frontend_build()
    
    print_banner(host, port)
    
    if open_browser:
        def _open():
            time.sleep(1.2)
            display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
            webbrowser.open(f"http://{display_host}:{port}")
        threading.Thread(target=_open, daemon=True).start()

    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

def main():
    parser = argparse.ArgumentParser(
        description="Host the complete NTC Darta-Chalan Digitization System"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")
    parser.add_argument("--dev", action="store_true", help="Run with concurrent Vite dev server on port 3000")
    parser.add_argument("--build-frontend", action="store_true", help="Force rebuild frontend production bundle")
    parser.add_argument("--seed", action="store_true", help="Force re-seed initial database data")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")

    args = parser.parse_args()

    # 1. Ensure .env
    check_and_setup_env()

    # 2. Ensure storage directories
    ensure_storage_directories()

    # 3. Ensure dependencies
    check_and_install_dependencies()

    # 4. Database migrations and initial seed
    ensure_database_and_seed(force_seed=args.seed)

    # 3. Handle optional force frontend build
    if args.build_frontend:
        ensure_frontend_build(force_build=True)

    # 4. Launch server
    if args.dev:
        run_dev_servers(host=args.host, port=args.port)
    else:
        run_production_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            open_browser=not args.no_browser
        )

if __name__ == "__main__":
    main()
