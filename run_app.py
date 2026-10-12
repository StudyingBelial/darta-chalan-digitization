#!/usr/bin/env python3
"""
=============================================================================
 Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
 Universal Application Runner (Exclusively Docker Containerized)
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
import socket
from pathlib import Path

# Configure UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = ROOT_DIR / "storage"

def get_local_ip() -> str:
    """Detect LAN / local network IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.3)
        # Connect to public DNS to resolve preferred outbound interface IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_banner(frontend_port: int, backend_port: int, smtp_port: int):
    local_ip = get_local_ip()
    
    print("\n" + "=" * 76)
    print("  [NTC] NEPAL TELECOM CORPORATION")
    print("  Darta-Chalan Digitization System (दर्ता-चलानी डिजिटल प्रणाली)")
    print("=" * 76)
    print("  * Deployment Mode    : Exclusively Docker Containerized")
    print("  * Database           : PostgreSQL 16 (Container: ntc_digitization_db)")
    print(f"  * Web Portal (Local) : http://localhost:{frontend_port}")
    print(f"  * Web Portal (LAN)   : http://{local_ip}:{frontend_port}  <-- Share on office network")
    print(f"  * REST API Docs      : http://localhost:{backend_port}/docs (or http://{local_ip}:{backend_port}/docs)")
    print(f"  * SMTP Scanner Intake: smtp://{local_ip}:{smtp_port}")
    print("-" * 76)
    print("  Default System Administrator Credentials (Auto-Seeded):")
    print("     * Email    : admin@ntc.net.np")
    print("     * Password : Admin@123456")
    print("     * Role     : SYSTEM_ADMIN")
    print("=" * 76)
    print("  Starting containers... Press Ctrl+C at any time to shut down gracefully.\n")

def check_docker_available():
    """Verify Docker CLI and Docker Engine are running."""
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        print("\n[ERROR] Docker is not installed or not found in system PATH!")
        print("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
        sys.exit(1)

    try:
        result = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        if result.returncode != 0:
            print("\n[ERROR] Docker Engine is not running!")
            print("Please open 'Docker Desktop' and wait until it indicates 'Engine running'.")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Could not communicate with Docker: {e}")
        sys.exit(1)

def ensure_env_and_dirs():
    """Verify .env exists and storage directories are created."""
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("[SETUP] Creating .env from .env.example...")
        shutil.copyfile(env_example, env_file)
        print("[SUCCESS] .env initialized.")

    for sub in ["uploads/darta", "uploads/chalan", "uploads/inbound", "logs"]:
        (STORAGE_DIR / sub).mkdir(parents=True, exist_ok=True)

    # Clean up obsolete SQLite db if found
    db_file = ROOT_DIR / "digitization.db"
    if db_file.exists():
        try:
            db_file.unlink()
            print("[CLEANUP] Removed legacy SQLite file digitization.db (system uses PostgreSQL).")
        except Exception:
            pass

def read_ports_from_env():
    """Read port mappings from .env file or default values."""
    env_file = ROOT_DIR / ".env"
    frontend_port = 3000
    backend_port = 8000
    smtp_port = 1025

    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    if line.startswith("FRONTEND_PORT="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.isdigit():
                            frontend_port = int(val)
                    elif line.startswith("PORT="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.isdigit():
                            backend_port = int(val)
                    elif line.startswith("SMTP_SCANNER_PORT="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.isdigit():
                            smtp_port = int(val)
        except Exception:
            pass

    return frontend_port, backend_port, smtp_port

def open_browser_delayed(url: str, delay: float = 3.5):
    """Open web browser in background after container startup."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()

def main():
    parser = argparse.ArgumentParser(
        description="NTC Darta-Chalan Digitization System — Docker Runner"
    )
    parser.add_argument("--down", action="store_true", help="Stop and remove all running containers")
    parser.add_argument("--logs", action="store_true", help="View and follow live logs of running containers")
    parser.add_argument("--no-build", action="store_true", help="Start containers without rebuilding images")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")
    parser.add_argument("--detach", "-d", action="store_true", help="Run containers in background")

    args = parser.parse_args()

    # 1. Verify Docker environment
    check_docker_available()

    # 2. Verify environment files and storage
    ensure_env_and_dirs()

    # 3. Read configured ports
    frontend_port, backend_port, smtp_port = read_ports_from_env()

    # Handle --down
    if args.down:
        print("[DOCKER] Stopping all Darta-Chalan containers...")
        subprocess.run(["docker", "compose", "down"], cwd=str(ROOT_DIR))
        print("[SUCCESS] Containers stopped.")
        return

    # Handle --logs
    if args.logs:
        print("[DOCKER] Tailing container logs (Ctrl+C to exit)...")
        subprocess.run(["docker", "compose", "logs", "-f"], cwd=str(ROOT_DIR))
        return

    # 4. Print user-friendly banner
    print_banner(frontend_port, backend_port, smtp_port)

    # 5. Open browser automatically
    if not args.no_browser and not args.detach:
        open_browser_delayed(f"http://localhost:{frontend_port}")

    # 6. Build command
    cmd = ["docker", "compose", "up"]
    if not args.no_build:
        cmd.append("--build")
    if args.detach:
        cmd.append("-d")

    try:
        subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)
    except KeyboardInterrupt:
        print("\n" + "=" * 76)
        print("  [SHUTDOWN] Stopping all Docker containers safely...")
        print("=" * 76)
        subprocess.run(["docker", "compose", "down"], cwd=str(ROOT_DIR))
        print("  [SUCCESS] All services stopped cleanly.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Docker Compose exited with error: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
