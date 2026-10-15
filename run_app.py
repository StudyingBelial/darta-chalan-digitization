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
CERTS_DIR = ROOT_DIR / "certs"

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

def ensure_ssl_certs(domain_name: str = ""):
    """Verify SSL certificates exist in ./certs, or auto-generate self-signed certs."""
    privkey_path = CERTS_DIR / "privkey.pem"
    fullchain_path = CERTS_DIR / "fullchain.pem"
    generate_script = ROOT_DIR / "scripts" / "generate_ssl.py"

    if not privkey_path.exists() or not fullchain_path.exists():
        print("[SSL] SSL certificates missing in ./certs/. Auto-generating self-signed certificate...")
        cmd = [sys.executable, str(generate_script)]
        if domain_name:
            cmd.append(domain_name)
        subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)
        print("[SSL] Self-signed certificate created successfully.")
    elif domain_name:
        try:
            from cryptography import x509
            with open(fullchain_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            sans = [str(x.value) for x in san_ext.value]
            if domain_name not in sans:
                print(f"[SSL] Updating SSL certificate to include domain: {domain_name}...")
                subprocess.run([sys.executable, str(generate_script), domain_name], cwd=str(ROOT_DIR), check=True)
        except Exception:
            pass

def print_banner(cfg: dict, is_ssl: bool = False, active_domain: str = ""):
    local_ip = get_local_ip()
    db_port = cfg.get("db_port", 5433)
    backend_port = cfg.get("backend_port", 8000)
    smtp_port = cfg.get("smtp_port", 1025)
    frontend_port = cfg.get("frontend_port", 3000)
    http_port = cfg.get("http_port", 80)
    https_port = cfg.get("https_port", 443)
    
    print("\n" + "=" * 76)
    print("  [NTC] NEPAL TELECOM CORPORATION")
    print("  Darta-Chalan Digitization System (दर्ता-चलानी डिजिटल प्रणाली)")
    print("=" * 76)
    
    if is_ssl:
        ssl_port_suffix = f":{https_port}" if https_port != 443 else ""
        http_port_suffix = f":{http_port}" if http_port != 80 else ""
        print("  * Deployment Mode    : Exclusively Docker (Secure HTTPS / TLS)")
        print(f"  * Database           : PostgreSQL 16 (Container: ntc_digitization_db, Port: {db_port})")
        print(f"  * Web Portal (Local) : https://localhost{ssl_port_suffix}")
        print(f"  * Web Portal (LAN)   : https://{local_ip}{ssl_port_suffix}  <-- Share on office network")
        if active_domain:
            print(f"  * Web Portal (Domain): https://{active_domain}{ssl_port_suffix}  <-- Custom Domain")
        print(f"  * HTTP Auto-Redirect : http://localhost{http_port_suffix} -> Redirects to HTTPS")
        print(f"  * REST API Docs (LAN): https://{local_ip}{ssl_port_suffix}/docs")
    else:
        print("  * Deployment Mode    : Exclusively Docker Containerized (HTTP)")
        print(f"  * Database           : PostgreSQL 16 (Container: ntc_digitization_db, Port: {db_port})")
        print(f"  * Web Portal (Local) : http://localhost:{frontend_port}")
        print(f"  * Web Portal (LAN)   : http://{local_ip}:{frontend_port}  <-- Share on office network")
        print(f"  * REST API Docs (LAN): http://{local_ip}:{frontend_port}/docs (or http://{local_ip}:{backend_port}/docs)")

    print(f"  * SMTP Scanner Intake: smtp://{local_ip}:{smtp_port}")
    print("-" * 76)
    print("  Default System Administrator Credentials (Auto-Seeded):")
    print("     * Email    : admin@ntc.net.np")
    print("     * Password : Admin@123456")
    print("     * Role     : SYSTEM_ADMIN")
    print("=" * 76)
    if is_ssl:
        print("  [SSL NOTE] Using self-signed SSL? If browser shows 'Not Secure', click")
        print("             'Advanced' -> 'Proceed to localhost' to open the secure app.")
        print("-" * 76)
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

        # On Windows, if repository is on a non-C drive (e.g. D:), ensure it is mounted in docker-desktop VM
        if sys.platform == "win32":
            drive = ROOT_DIR.drive
            if drive and drive.upper() != "C:":
                d_letter = drive.rstrip(":").lower()
                try:
                    subprocess.run(
                        ["wsl", "-d", "docker-desktop", "-u", "root", "mount", "-t", "drvfs", f"{drive}", f"/mnt/host/{d_letter}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False
                    )
                except Exception:
                    pass
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

def read_config_from_env():
    """Read port mappings, SSL mode, and domain configuration from .env file."""
    env_file = ROOT_DIR / ".env"
    cfg = {
        "frontend_port": 3000,
        "backend_port": 8000,
        "smtp_port": 1025,
        "db_port": 5433,
        "ssl_enabled": False,
        "domain_name": "",
        "http_port": 80,
        "https_port": 443,
    }

    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == "FRONTEND_PORT" and val.isdigit():
                        cfg["frontend_port"] = int(val)
                    elif key == "PORT" and val.isdigit():
                        cfg["backend_port"] = int(val)
                    elif key == "SMTP_SCANNER_PORT" and val.isdigit():
                        cfg["smtp_port"] = int(val)
                    elif key == "DB_PORT" and val.isdigit():
                        cfg["db_port"] = int(val)
                    elif key == "SSL_ENABLED":
                        cfg["ssl_enabled"] = val.lower() in ("true", "1", "yes", "on")
                    elif key == "DOMAIN_NAME":
                        cfg["domain_name"] = val
                    elif key == "HTTP_PORT" and val.isdigit():
                        cfg["http_port"] = int(val)
                    elif key == "HTTPS_PORT" and val.isdigit():
                        cfg["https_port"] = int(val)
        except Exception:
            pass

    return cfg

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
    parser.add_argument("--ssl", "--https", action="store_true", help="Enable secure HTTPS/SSL mode (ports 80 & 443)")
    parser.add_argument("--domain", type=str, default="", help="Custom domain name (e.g. darta.ntc.net.np or darta.local)")

    args = parser.parse_args()

    # 1. Verify Docker environment
    check_docker_available()

    # 2. Verify environment files and storage
    ensure_env_and_dirs()

    # 3. Read configured settings
    cfg = read_config_from_env()

    # Determine SSL mode and domain name (CLI flag overrides .env)
    is_ssl = args.ssl or cfg["ssl_enabled"]
    active_domain = (args.domain or cfg["domain_name"]).strip()

    compose_files = ["-f", "docker-compose.public.yml"] if is_ssl else ["-f", "docker-compose.yml"]

    # Handle --down (stops both standard and SSL compose stacks cleanly)
    if args.down:
        print("[DOCKER] Stopping all Darta-Chalan containers...")
        subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.public.yml", "down"], cwd=str(ROOT_DIR))
        print("[SUCCESS] Containers stopped.")
        return

    # Handle --logs
    if args.logs:
        print("[DOCKER] Tailing container logs (Ctrl+C to exit)...")
        subprocess.run(["docker", "compose", *compose_files, "logs", "-f"], cwd=str(ROOT_DIR))
        return

    # If SSL is enabled, ensure certificates are ready and set domain environment
    if is_ssl:
        ensure_ssl_certs(active_domain)
        if active_domain:
            os.environ["DOMAIN_NAME"] = active_domain

    # 4. Print user-friendly banner
    print_banner(cfg, is_ssl, active_domain)

    # 5. Open browser automatically
    if not args.no_browser and not args.detach:
        if is_ssl:
            https_port = cfg["https_port"]
            port_suffix = f":{https_port}" if https_port != 443 else ""
            if active_domain and active_domain != "localhost":
                browser_url = f"https://{active_domain}{port_suffix}"
            else:
                browser_url = f"https://localhost{port_suffix}"
        else:
            browser_url = f"http://localhost:{cfg['frontend_port']}"
        open_browser_delayed(browser_url)

    # 6. Build command
    cmd = ["docker", "compose", *compose_files, "up"]
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
        subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.public.yml", "down"], cwd=str(ROOT_DIR))
        print("  [SUCCESS] All services stopped cleanly.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Docker Compose exited with error: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
