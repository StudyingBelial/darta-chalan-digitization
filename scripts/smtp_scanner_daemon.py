#!/usr/bin/env python3
"""
=============================================================================
 Nepal Telecom Corporation (NTC) — Standalone Inbound SMTP Scanner Daemon
=============================================================================
This standalone service runs as a dedicated background daemon to ingest
scanned documents directly from Canon imageRUNNER / network scanner appliances
and inter-office emails over standard SMTP/ESMTP (RFC 5321).

Usage:
    python scripts/smtp_scanner_daemon.py
    python scripts/smtp_scanner_daemon.py --host 0.0.0.0 --port 1025
=============================================================================
"""

import sys
import os
import asyncio
import argparse
import signal
from pathlib import Path

# Set project root on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import settings
from backend.app.services.smtp_scanner import smtp_scanner_service
from backend.app.core.logger import logger

def print_scanner_banner(host: str, port: int):
    print("\n" + "=" * 76)
    print("  🇳🇵  NEPAL TELECOM CORPORATION (NTC)")
    print("  📠  Inbound Hardware Scanner & Email Ingestion Daemon (SMTP/ESMTP)")
    print("=" * 76)
    print(f"  📡 Bind Interface   : {host}")
    print(f"  🔌 Listening Port   : {port}")
    print(f"  🖨️  Scanner Protocols: Canon imageRUNNER, CanoScan, HP, Ricoh, Xerox Scan-to-Email")
    print(f"  📄 Target Queue     : Central Darta Inbound Intake Queue")
    print(f"  🏢 Default Office ID: {settings.SMTP_SCANNER_DEFAULT_OFFICE_ID}")
    print(f"  🌐 Allowed Domains  : {settings.SMTP_SCANNER_ALLOWED_DOMAINS or 'All domains allowed'}")
    print("-" * 76)
    print("  Ready to receive hardware scanner transmissions. Press Ctrl+C to exit.\n")

async def main_async(host: str, port: int):
    started = await smtp_scanner_service.start(host=host, port=port)
    if not started:
        print(f"❌ Could not bind SMTP server to {host}:{port}. Check permissions or port usage.")
        sys.exit(1)

    print_scanner_banner(host, port)

    stop_event = asyncio.Event()

    def _signal_handler():
        print("\n🛑 Shutdown signal received. Closing SMTP listener...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Signal handlers not implemented on Windows event loop for add_signal_handler
            pass

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await smtp_scanner_service.stop()
        print("✅ SMTP Scanner Daemon terminated cleanly.")

def main():
    parser = argparse.ArgumentParser(description="NTC Inbound SMTP Scanner Daemon")
    parser.add_argument("--host", default=settings.SMTP_SCANNER_HOST, help="Host address to bind")
    parser.add_argument("--port", type=int, default=settings.SMTP_SCANNER_PORT, help="Port to listen on")
    args = parser.parse_args()

    try:
        asyncio.run(main_async(args.host, args.port))
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()
