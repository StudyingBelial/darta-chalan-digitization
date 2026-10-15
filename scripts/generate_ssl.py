#!/usr/bin/env python3
"""
=============================================================================
 Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
 Intranet & Local SSL/TLS Certificate Generator
=============================================================================
Generates self-signed X.509 SSL certificates with Subject Alternative Names (SAN)
for localhost, local network IP (e.g. 192.168.1.15), and custom domains.
"""

import sys
import socket
import datetime
import ipaddress
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CERTS_DIR = ROOT_DIR / "certs"

def get_local_ip() -> str:
    """Detect LAN / local network IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.3)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_certificates(extra_domains: list[str] | None = None):
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
    except ImportError:
        print("[ERROR] 'cryptography' library is not installed.")
        print("Please run: pip install cryptography")
        sys.exit(1)

    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    privkey_path = CERTS_DIR / "privkey.pem"
    fullchain_path = CERTS_DIR / "fullchain.pem"

    local_ip = get_local_ip()
    domains = ["localhost", "127.0.0.1", local_ip]
    if extra_domains:
        domains.extend(extra_domains)

    print("\n" + "=" * 70)
    print("  [NTC] Darta-Chalan Intranet SSL Certificate Generator")
    print("=" * 70)
    print(f"  * Localhost IP       : 127.0.0.1")
    print(f"  * Detected LAN IP    : {local_ip}")
    print(f"  * Output Directory   : {CERTS_DIR}")
    print(f"  * Protected Hostnames: {', '.join(set(domains))}")
    print("-" * 70)

    # 1. Generate Private Key
    print("[1/3] Generating 2048-bit RSA private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Build Certificate with Subject Alternative Names (SAN)
    print("[2/3] Building X.509 certificate with Subject Alternative Names...")
    san_entries: list[x509.GeneralName] = [
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]

    try:
        lan_ip_obj = ipaddress.IPv4Address(local_ip)
        if lan_ip_obj not in [e.value for e in san_entries if isinstance(e, x509.IPAddress)]:
            san_entries.append(x509.IPAddress(lan_ip_obj))
    except ValueError:
        pass

    if extra_domains:
        for d in extra_domains:
            d = d.strip()
            if not d:
                continue
            try:
                ip_obj = ipaddress.ip_address(d)
                san_entries.append(x509.IPAddress(ip_obj))
            except ValueError:
                san_entries.append(x509.DNSName(d))

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "NP"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Bagmati"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Kathmandu"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Nepal Telecom Corporation"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT Department"),
        x509.NameAttribute(NameOID.COMMON_NAME, local_ip),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))  # Valid for 10 years
        .add_extension(
            x509.SubjectAlternativeName(san_entries),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 3. Write Files
    print("[3/3] Saving certificate files...")
    with open(privkey_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(fullchain_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("\n" + "=" * 70)
    print("  [SUCCESS] SSL Certificates Generated Successfully!")
    print("=" * 70)
    print(f"  * Private Key        : {privkey_path}")
    print(f"  * Public Certificate : {fullchain_path}")
    print(f"  * Validity           : 10 Years (Expires: {(now + datetime.timedelta(days=3650)).strftime('%Y-%m-%d')})")
    print("\nYou can now launch public HTTPS containers with:")
    print("  docker compose -f docker-compose.public.yml up -d --build")
    print(f"Then visit: https://{local_ip} or https://localhost")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    extra = sys.argv[1:] if len(sys.argv) > 1 else None
    generate_certificates(extra)
