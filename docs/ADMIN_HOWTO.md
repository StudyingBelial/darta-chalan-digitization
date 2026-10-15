# Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
# Complete Administrator How-To & Operations Guide

> **System Name:** Darta-Chalan Digitization Platform (दर्ता-चलानी डिजिटल प्रणाली)  
> **Target Audience:** System Administrators (`SYSTEM_ADMIN`), Office Administrators (`OFFICE_ADMIN`), Network/IT Engineers  
> **Classification:** Internal IT Operations Manual

---

## Table of Contents
1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Prerequisites & Initial Installation](#2-prerequisites--initial-installation)
3. [Configuration & Environment Variables (.env)](#3-configuration--environment-variables-env)
4. [Inbound SMTP Scanner Setup (Scan-to-Email / Network MFPs)](#4-inbound-smtp-scanner-setup-scan-to-email--network-mfps)
5. [Outbound Email Notification System](#5-outbound-email-notification-system)
6. [Hardware Scanner & Windows Bridge Integration](#6-hardware-scanner--windows-bridge-integration)
7. [User & Role-Based Access Control (RBAC) Management](#7-user--role-based-access-control-rbac-management)
8. [Master Data Management (Offices, Departments, Officers, Fiscal Years)](#8-master-data-management)
9. [Network Deployment, Intranet LAN & SSL/HTTPS Configuration](#9-network-deployment-intranet-lan--sslhttps-configuration)
10. [Database Management, Backup & Disaster Recovery](#10-database-management-backup--disaster-recovery)
11. [System Audit Logs & Security Monitoring](#11-system-audit-logs--security-monitoring)
12. [Troubleshooting & Administrator FAQ](#12-troubleshooting--administrator-faq)

---

## 1. System Overview & Architecture

The Nepal Telecom Darta-Chalan Digitization System is an enterprise document intake, sequential numbering, OCR indexing, and document-routing platform.

### Core Architectural Components:
- **Frontend Web Portal (Port 3000 / 80):** React 18, TypeScript, Vite, served via high-performance Nginx.
- **Backend REST API (Port 8000):** FastAPI (Python 3.10+), SQLAlchemy 2.0 ORM, Pydantic v2 validation.
- **Relational Database (Port 5433 host / 5432 container):** PostgreSQL 16 Alpine with transactional ACID safety and automated Alembic schema migrations.
- **Inbound ESMTP Socket Daemon (Port 1025 / 25):** Asynchronous RFC 5321 mail transfer agent for zero-click MFP scan-to-email document intake.
- **OCR Engine:** Tesseract OCR with dual English and Devanagari (Nepali) language parsing support.
- **Local Scanner Bridge (Port 8080):** Windows WIA/TWAIN hardware interface daemon for physical USB desktop scanners (Canon imageFORMULA, CanoScan).

---

## 2. Prerequisites & Initial Installation

### Minimum Server Requirements:
- **Operating System:** Windows Server 2016+, Windows 10/11 Pro, or Ubuntu 22.04+ LTS.
- **CPU:** 4 Cores (Recommended for concurrent OCR processing).
- **RAM:** 8 GB minimum (16 GB recommended for high document volume).
- **Disk Space:** 50 GB+ SSD storage (mounted on `/storage/uploads` for partitioned document archive).
- **Software Dependencies:** Docker Desktop (with Docker Compose v2+) or native Docker Engine.

### Quick Launch Instructions:
1. Open PowerShell or Command Prompt in the repository root directory:
   ```powershell
   cd c:\Users\asus\Desktop\NTC\darta-chalan-digitization
   ```
2. Prepare the environment file:
   ```powershell
   copy .env.example .env
   ```
3. Launch the container stack using the automated Python orchestrator:
   ```powershell
   python run_app.py
   ```
   *Alternatively, launch directly via Docker Compose:*
   ```powershell
   docker compose up --build -d
   ```
4. Verify all containers are healthy:
   ```powershell
   docker ps
   ```
   You should observe three active containers:
   - `ntc_digitization_db` (Up, Healthy)
   - `ntc_digitization_backend` (Up, Healthy)
   - `ntc_digitization_frontend` (Up, Healthy)

---

## 3. Configuration & Environment Variables (.env)

The root `.env` file governs system runtime behavior. Administrators must review and tune the following sections:

```ini
# ==============================================================================
# 1. System & Port Configuration
# ==============================================================================
PROJECT_NAME="Nepal Telecom Darta-Chalan Digitization System"
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000              # FastAPI backend container port
FRONTEND_PORT=3000     # Set to 80 if direct LAN access without port :3000 is desired
DB_PORT=5433           # External host port mapped to avoid conflicting with existing Postgres

# ==============================================================================
# 2. Database Connection
# ==============================================================================
POSTGRES_DB=darta_chalan_db
POSTGRES_USER=ntc_admin
POSTGRES_PASSWORD=ntc_secure_password_2081
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://ntc_admin:ntc_secure_password_2081@db:5432/darta_chalan_db

# ==============================================================================
# 3. Security & Token Lifespans
# ==============================================================================
# Generate a production key using: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=CHANGE_THIS_TO_A_STRONG_RANDOM_SECRET_KEY_IN_PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120     # Session token lifetime
REFRESH_TOKEN_EXPIRE_HOURS=24       # Sliding session refresh lifetime

# ==============================================================================
# 4. Storage & OCR Engine
# ==============================================================================
UPLOAD_DIR=/app/storage/uploads
MAX_UPLOAD_SIZE_MB=25               # Maximum single document attachment size
TESSERACT_CMD=/usr/bin/tesseract

# ==============================================================================
# 5. Inbound SMTP Hardware Scanner Settings
# ==============================================================================
SMTP_SCANNER_ENABLED=true
SMTP_SCANNER_HOST=0.0.0.0
SMTP_SCANNER_PORT=1025
SMTP_SCANNER_MAX_MESSAGE_MB=25
SMTP_SCANNER_ALLOWED_DOMAINS=ntc.net.np,gov.np
SMTP_SCANNER_DEFAULT_OFFICE_ID=1

# ==============================================================================
# 6. Outbound SMTP Notification Gateway
# ==============================================================================
OUTBOUND_EMAIL_ENABLED=false
OUTBOUND_SMTP_HOST=smtp.ntc.net.np
OUTBOUND_SMTP_PORT=587
OUTBOUND_SMTP_USER=
OUTBOUND_SMTP_PASSWORD=
OUTBOUND_SMTP_FROM=darta@ntc.net.np
OUTBOUND_SMTP_USE_TLS=true
```

---

## 4. Inbound SMTP Scanner Setup (Scan-to-Email / Network MFPs)

### What It Does:
The platform features an embedded **RFC 5321 ESMTP server** (`backend/app/services/smtp_scanner.py`) listening on port `1025` (or configurable standard port `25`). This eliminates the need for third-party cloud mailboxes or polling scripts. When an office clerk scans a paper letter on a network printer (Canon, HP, Ricoh, Xerox), the printer dispatches the PDF directly to this socket. The system:
1. Ingests the raw MIME email stream.
2. Detects the hardware scanner signature (`Canon imageRUNNER`, `CanoScan`, `Ricoh`, etc.).
3. Extracts PDF/TIFF attachments.
4. Generates a cryptographic SHA-256 fingerprint.
5. Performs immediate optical character recognition (OCR) and candidate field extraction.
6. Places the document into the **Inbound Queue** for staff review and one-click Darta conversion.

### Step-by-Step MFP Printer Configuration (Canon imageRUNNER Example):
1. Access the printer’s web administrative console via its browser IP (e.g., `http://192.168.1.200`).
2. Log in with printer administrator credentials.
3. Navigate to **System Management Settings** > **Network Settings** > **TCP/IP Settings** > **SMTP Settings** (or **E-Mail/I-Fax Settings**).
4. Enter the following parameters:
   - **SMTP Server / Host Name:** Enter the LAN IP address of your Darta-Chalan Server (e.g., `192.168.1.31` or DNS name `darta.ntc.net.np`).
   - **SMTP Port Number:** `1025` (or `25` if configured in production).
   - **Authentication:** Disabled (None / Anonymous) for internal office subnet, or set matching local network credentials.
   - **SSL/TLS (STARTTLS):** Disabled for internal port 1025 plain ESMTP, or Enabled if routing over TLS proxy.
   - **Printer Email Address (Sender):** `scanner.canon@ntc.net.np` or `branch.reception@ntc.net.np`.
5. Navigate to the printer's **Address Book (One-Touch Speed Dial)**:
   - **Destination Name:** `Darta Intake System`
   - **Destination Type:** E-Mail
   - **Email Address:** `intake@ntc.net.np` (must match an allowed domain in `.env`).
6. Save and perform a test transmission from the printer glass.

### Running as a Standalone Inbound Scanner Daemon:
If you wish to decouple the scanner ingestion service from Docker or run it on a dedicated branch intake workstation:
```powershell
python scripts/smtp_scanner_daemon.py --host 0.0.0.0 --port 1025
```

### Verifying and Testing the Inbound SMTP Scanner:
1. Log into the Web Portal as `SYSTEM_ADMIN` or `OFFICE_ADMIN`.
2. Navigate to **Inbound Queue** in the sidebar.
3. Observe the **SMTP Scanner Status Card** in the top-right header:
   - Green badge: `SMTP Listener Active (0.0.0.0:1025)`
   - Displays real-time message counter, last sender, and timestamp.
4. Click **Send Test Hardware Scan**:
   - Dispatches a realistic Canon imageRUNNER multipart MIME scanned payload through the loopback socket.
   - Verify the intake queue immediately shows the new incoming letter with an OCR confidence rating.

---

## 5. Outbound Email Notification System

### Purpose:
Provides automated delivery of:
- Document forwarding notifications (e.g., "Darta #104 has been forwarded to your department by Administration").
- Internal review task assignments.
- Account password resets.

### Configuration:
In `.env`, configure your institutional NTC mail server:
```ini
OUTBOUND_EMAIL_ENABLED=true
OUTBOUND_SMTP_HOST=smtp.ntc.net.np
OUTBOUND_SMTP_PORT=587
OUTBOUND_SMTP_USER=darta-system@ntc.net.np
OUTBOUND_SMTP_PASSWORD=YourCorporateAppPassword
OUTBOUND_SMTP_FROM=darta@ntc.net.np
OUTBOUND_SMTP_USE_TLS=true
```
When `OUTBOUND_EMAIL_ENABLED=true`, `backend/app/services/notification_service.py` relays email notifications simultaneously while recording in-app notification drawer alerts.

---

## 6. Hardware Scanner & Windows Bridge Integration

The system accommodates workstations connected directly to USB desktop scanners (e.g., Canon imageFORMULA DR-C225, CanoScan LiDE 400).

### Launching the Windows Scanner Bridge:
1. On the reception PC connected via USB to the Canon scanner, ensure the official Canon Windows driver/WIA is installed.
2. Execute the bridge script:
   ```powershell
   python scripts/windows_scanner_bridge.py
   ```
3. The bridge listens on `http://127.0.0.1:8080` with CORS support.
4. When any user opens the **Canon & Hardware Document Scanner** modal in the web portal, the browser auto-detects `http://127.0.0.1:8080/health`:
   - Connection Mode switches from Direct Driver to **Connected to Canon Scanner via Local Windows Bridge (Port 8080)**.
   - Hardware controls for Automatic Document Feeder (ADF), Duplex, 150/300/600 DPI, Auto-Deskew, and Contrast Enhancement become active.

---

## 7. User & Role-Based Access Control (RBAC) Management

### User Roles & Permission Hierarchy:

| Feature / Action | `STAFF` | `OFFICE_ADMIN` | `SYSTEM_ADMIN` |
| :--- | :---: | :---: | :---: |
| Register Incoming Darta (`darta:create`) | ✅ | ✅ | ✅ |
| Forward Darta to another Department (`darta:forward`) | ✅ | ✅ | ✅ |
| Issue Outgoing Chalan (`chalan:create`) | ✅ | ✅ | ✅ |
| Forward Outgoing Chalan (`chalan:forward`) | ✅ | ✅ | ✅ |
| Search & OCR Keyword Search (`darta:search`, `chalan:search`) | ✅ | ✅ | ✅ |
| Download Document Attachments (`document:download`) | ✅ | ✅ | ✅ |
| Update Self Profile & Password (`users:self_update`) | ✅ | ✅ | ✅ |
| Create & Manage Users for Office (`users:create`, `users:update`) | ❌ | ✅ | ✅ |
| Disable/Enable User Accounts (`users:disable`) | ❌ | ✅ | ✅ |
| Reset Other Users' Passwords (`users:other_update`) | ❌ | ✅ | ✅ |
| Create Officers & Departments (`officers:create`, `departments:create`) | ❌ | ✅ | ✅ |
| Create Offices & Branches (`offices:create`) | ❌ | ❌ | ✅ |
| Create New Financial Year (`financial_year:create`) | ❌ | ❌ | ✅ |
| View System & Audit Logs (`logs:view`) | ❌ | ✅ | ✅ |

### How to Create a New User:
1. Log in as an Administrator (`SYSTEM_ADMIN` or `OFFICE_ADMIN`).
2. Navigate to **Users & Security** (`/users`).
3. Click the **+ Create New User** button.
4. Provide:
   - **Full Name:** e.g., `Suman Shrestha`
   - **Official Email:** e.g., `suman.s@ntc.net.np` (must be unique).
   - **Assigned Role:** Select `STAFF`, `OFFICE_ADMIN`, or `SYSTEM_ADMIN`.
   - **Office Assignment:** Select the designated office branch.
   - **Temporary Password:** Minimum 8 characters with at least one uppercase, lowercase, number, and special character.
5. Click **Create User Account**.

### How to Reset an Employee's Forgotten Password:
1. Navigate to **Users & Security**.
2. Locate the user in the table and click the **Key icon (Reset Password)**.
3. Enter the new temporary password.
4. Click **Reset Password**.
5. Inform the user to log in and update their password under their **User Profile** page.

### How to Deactivate/Suspend a User Account:
1. In the **Users & Security** table, locate the user.
2. Toggle the **Active / Suspended** toggle switch.
3. Disabled users are rejected at login with HTTP 400 (`User account is disabled`) and active refresh tokens are immediately revoked.

---

## 8. Master Data Management

System Administrators control the organizational taxonomy via **Master Data** (`/master-data`):

1. **Offices & Branches (`/offices`):**
   - Represents physical branches (e.g., `NTC Central Office - Bhadrakali`, `Patan Branch - Jawalakhel`, `Pokhara Regional Directorate`).
   - Darta and Chalan sequential numbers reset and partition per office.
2. **Internal Departments (`/departments`):**
   - Organizational units (e.g., `Administration Department`, `Billing & Revenue`, `Transmission Directorate`, `IT Operations`).
3. **Officers (`/officers`):**
   - Designations/personnel designated as recipients of correspondence (e.g., `Chief Administrative Officer`, `Director of Telecom Operations`).
4. **Financial Years (`/financial-year`):**
   - Formatted in Nepalese Bikram Sambat fiscal cycles (e.g., `2080/81`, `2081/82`).
   - The platform includes automated financial year computation (`DateService.get_nepali_fiscal_year()`) where Shrawan 1 triggers a new fiscal year.

---

## 9. Network Deployment, Intranet LAN & SSL/HTTPS Configuration

### Option A: Local Office Intranet Access (HTTP Port 3000 or 80)
1. Configure Windows Firewall on host machine by running as Administrator:
   ```powershell
   powershell -File scripts/setup_firewall_rules.ps1
   ```
2. Start containers: `python run_app.py`.
3. Colleagues on the same office Wi-Fi or Ethernet LAN access the portal via:
   `http://<SERVER_LAN_IP>:3000` (e.g. `http://192.168.1.31:3000`).
4. To allow users to browse without typing `:3000`, set `FRONTEND_PORT=80` in `.env`.

### Option B: Production Public HTTPS Deployment (Nginx Reverse Proxy)
For intranet or public internet deployments requiring HTTPS with automatic HTTP-to-HTTPS redirect:
1. Generate internal self-signed intranet certificates or copy your CA certificates:
   ```powershell
   python scripts/generate_ssl.py
   ```
   *(For official domains such as `darta.ntc.net.np`, place your CA-signed `fullchain.pem` and `privkey.pem` into the `certs/` folder).*
2. Start the production public stack:
   ```powershell
   docker compose -f docker-compose.public.yml up -d --build
   ```
3. All traffic on port 80 is automatically 301-redirected to port 443 with TLS 1.2/1.3 and security headers (HSTS, CSP, X-Frame-Options).

### Option C: Zero-Config Remote Access via Cloudflare Tunnel
To provide secure internet access without port forwarding or static public IPs:
```powershell
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d
docker compose logs cloudflare-tunnel
```

---

## 10. Database Management, Backup & Disaster Recovery

### Automated Storage Architecture:
- Document files are saved in `/app/storage/uploads/{type}/{YYYY}/{MM}/` with unique UUID timestamps.
- Every file's SHA-256 hash is computed and recorded in the database to guarantee tamper detection.

### Backing Up the PostgreSQL Database:
Execute an automated SQL dump from the running container:
```powershell
# On Windows PowerShell:
docker exec -t ntc_digitization_db pg_dump -U ntc_admin -d darta_chalan_db > backup_darta_chalan_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

### Restoring a Database Backup:
```powershell
docker exec -i ntc_digitization_db psql -U ntc_admin -d darta_chalan_db < backup_file.sql
```

### Backing Up Attached Documents:
The Docker volume `ntc_digitization_uploads` persists all physical files. To archive:
```powershell
docker run --rm -v ntc_digitization_uploads:/volume -v ${PWD}:/backup alpine tar -czf /backup/documents_backup.tar.gz -C /volume .
```

---

## 11. System Audit Logs & Security Monitoring

Under **Audit Logs** (`/logs`), Administrators can monitor every system transaction:
- **Traceability:** Every Darta creation, Chalan dispatch, document forwarding, user modification, and login attempt is written to the immutable `logs` table.
- **Filter by Severity:** Filter by `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.
- **Filter by User / Office:** Identify which user performed an action and the exact timestamp.
- **Direct Container Logs Inspection:**
  ```powershell
  python run_app.py --logs
  # Or:
  docker compose logs -f backend
  ```

---

## 12. Troubleshooting & Administrator FAQ

### Q1: The web portal displays "Network Error" or cannot connect to backend.
- **Solution:** Verify that `ntc_digitization_backend` is running:
  ```powershell
  docker compose ps
  ```
  Check backend logs for database migration failures:
  ```powershell
  docker compose logs backend
  ```

### Q2: Port 5433 or 3000 is already in use by another application.
- **Solution:** Edit `.env` and change `DB_PORT=5434` or `FRONTEND_PORT=3001`, then restart with `python run_app.py`.

### Q3: Scanned emails to port 1025 are rejected with "Relaying Denied".
- **Solution:** Check the recipient email domain against `SMTP_SCANNER_ALLOWED_DOMAINS` in `.env`. Ensure the printer sends to an address ending in `@ntc.net.np` or `@gov.np`.

### Q4: OCR text is blank or failing on scanned PDFs.
- **Solution:** Ensure the document is not an encrypted/password-protected PDF. Verify that the Docker container has Tesseract installed (`docker exec -it ntc_digitization_backend tesseract --version`).

---
*Document Version: 1.0.0 | Nepal Telecom Corporation IT Division*
