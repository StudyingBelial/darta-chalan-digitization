# Darta-Chalan Digitization System (दर्ता-चलानी डिजिटल प्रणाली)
### Nepal Telecom Corporation (NTC) — Enterprise Document Registration & Dispatch Platform

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6.svg?logo=typescript)](https://www.typescriptlang.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-GPLv3-yellow.svg)](LICENSE)

An enterprise-grade, production-ready full-stack system engineered specifically for digitizing, automating, and auditing **Darta (दर्ता - Incoming Document Registration)** and **Chalan (चलानी - Outgoing Document Dispatch)** workflows across Nepal Telecom Corporation (NTC) and governmental offices.

---

## 🚀 Quick Start (Single-Command Hosting)

The platform includes a universal Python host runner script (`run_app.py`) that handles environment setup, database migrations, initial seeding, frontend verification, and unified Uvicorn server hosting.

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13)
- **Node.js 18+** & **npm** (Required for compiling the frontend)
- **Tesseract OCR** (Optional; required for scanned document text extraction)

### 2. Install & Launch
```bash
# Clone the repository
git clone <repository-url>
cd darta-chalan-digitization

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Launch the entire application with one command
python run_app.py
```

Upon launching, the system automatically:
1. Creates `.env` from `.env.example` if not already present.
2. Applies Alembic database migrations (`alembic upgrade head`).
3. Seeds the initial organizational structure, active fiscal year, and default administrator account.
4. Verifies/compiles the React production bundle (`frontend/dist`).
5. Starts the unified server on **`http://localhost:8000`** and opens the web application in your browser.

---

## 🔑 Default Administrator Credentials

| Parameter | Value |
| :--- | :--- |
| **Portal URL** | [http://localhost:8000](http://localhost:8000) |
| **Email** | `admin@ntc.net.np` |
| **Password** | `Admin@123456` |
| **Role Type** | `SYSTEM_ADMIN` |

---

## 🛠️ CLI Options for `run_app.py`

| Flag | Description | Default |
| :--- | :--- | :--- |
| `--host` | Host interface address to bind | `0.0.0.0` |
| `--port` | Port number to listen on | `8000` |
| `--dev` | Launch backend with concurrent Vite dev server on port `3000` | `False` |
| `--reload` | Enable auto-reload on code modifications | `False` |
| `--build-frontend` | Force a fresh build of the React frontend | `False` |
| `--seed` | Force re-seeding of master data and admin account | `False` |
| `--no-browser` | Prevent automatic opening of the web browser | `False` |

**Examples:**
```bash
# Host on a custom port
python run_app.py --port 8080

# Run in Development Mode with live hot-reloading
python run_app.py --dev

# Force re-compile frontend and re-seed database
python run_app.py --build-frontend --seed
```

---

## 📐 Architecture & Key Features

```
darta-chalan-digitization/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST API Endpoints (Auth, Darta, Chalan, Users, etc.)
│   │   ├── controllers/         # API Controllers & request orchestration
│   │   ├── core/                # Config, Security (JWT/Bcrypt), Permissions & RBAC
│   │   ├── db/                  # Declarative base & SQLAlchemy 2.0 ORM models
│   │   ├── enums/               # System enums (USER_TYPE, DOCUMENT_STATUS, etc.)
│   │   ├── repositories/        # Data Access Layer (CRUD DB queries)
│   │   ├── schemas/             # Pydantic v2 DTOs & validation schemas
│   │   └── services/            # Core business logic services
│   └── scripts/seed.py          # Master data & administrator seeder
├── frontend/
│   ├── src/
│   │   ├── components/          # Modals (Scanner, OCR, Intake, Forwarding, Navbar)
│   │   ├── context/             # AuthContext & global state
│   │   ├── pages/               # Views (Dashboard, Darta, Chalan, Users, Logs, etc.)
│   │   ├── services/            # Axios API clients & authenticated blob downloaders
│   │   └── types/               # TypeScript interface definitions
│   └── dist/                    # Compiled production assets
├── storage/uploads/             # Secure partitioned document file storage
├── tests/                       # Pytest automated test suite
├── run_app.py                   # Single-command application host script
├── alembic.ini                  # Alembic migration configuration
├── requirements.txt             # Python backend dependencies
└── docker-compose.yml           # Multi-container orchestration
```

### Core System Features

1. **Document Workflow Management (`DocumentWorkflowService`)**:
   - Sequential auto-incrementing Darta/Chalan registration numbers isolated per office and financial year.
   - Dual Gregorian (A.D.) and Nepalese Bikram Sambat (B.S.) date support powered by `nepali-datetime`.
   - Automatic Nepalese Financial Year determination (Shrawan 1 start date).

2. **Optical Character Recognition (`OCRService`) & Global Search**:
   - Automatic text extraction from scanned PDF/image attachments using `pytesseract` and `Pillow`.
   - Full-text keyword search indexing across document metadata and extracted OCR content.
   - Filter by Nepalese Bikram Sambat date ranges (`from_date_bs`, `to_date_bs`), statuses, and sender/receiver.

3. **Inbound ESMTP Scanner & Network Scan-to-Email Intake (`SMTPServerService`)**:
   - Built-in asynchronous RFC 5321 ESMTP service listening on port `1025` (or configurable port `25` in production).
   - Real-time ingestion of physical scan dispatches from **Canon imageRUNNER**, **imageFORMULA**, **HP**, **Ricoh**, and **Xerox** network multi-function printers (MFPs).
   - Automatic MIME attachment extraction, SHA-256 fingerprinting, background OCR parsing with confidence metrics, and staff notification alerts.
   - Dedicated standalone scanner daemon (`python scripts/smtp_scanner_daemon.py`) for decoupled scanner ingestion.

4. **Hardware Scanner & Raw Upload Intake**:
   - Built-in **Canon / Universal TWAIN Hardware Scanner Modal** supporting multi-page ADF scanning, DPI control, contrast enhancement, and auto-deskew.
   - Unified intake workflow with candidate field auto-parsing and confidence scoring.

5. **Document Routing & Forwarding Audit Trail (`ForwardingService`)**:
   - Route documents between branches, internal departments, and designated officers with instructions and remarks.
   - Complete visual movement history timeline for every document.

5. **Administrative User Management & RBAC**:
   - Role-Based Access Control across `SYSTEM_ADMIN`, `OFFICE_ADMIN`, and `STAFF`.
   - User profile management, office assignments, account activation toggles, and direct administrative password resets.

6. **Cryptographic File Storage (`StorageService`)**:
   - Date-partitioned directory structure (`/storage/uploads/{type}/{YYYY}/{MM}/...`).
   - Automated **SHA-256 digital fingerprinting** and tamper verification.

7. **Governmental Compliance CSV Exports (`ExportService`)**:
   - Export standard **Darta Register (दर्ता किताब)** and **Chalan Register (चलानी किताब)** adhering to official Nepalese government formatting.

---

## 🐳 Docker Deployment

The platform is fully containerized with multi-stage Docker builds.

### Run with Docker Compose
```bash
# Build and start both Backend and Frontend containers
docker-compose up --build -d

# View service logs
docker-compose logs -f
```

- **Frontend Application**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`

---

## 🧪 Automated Testing

The codebase includes an extensive Pytest test suite covering authentication, auto-sequencing, document workflows, search, forwarding, and API routes.

```bash
# Run backend test suite
pytest

# Run tests with verbose output
pytest -v
```

---

## 🛡️ Security & Access Control Matrix

| Permission Code | `SYSTEM_ADMIN` | `OFFICE_ADMIN` | `STAFF` | Description |
| :--- | :---: | :---: | :---: | :--- |
| `users:create` | ✅ | ✅ | ❌ | Create new user accounts |
| `users:update` | ✅ | ✅ | ❌ | Edit user profiles & reset passwords |
| `users:disable` | ✅ | ✅ | ❌ | Enable/disable user accounts |
| `offices:create` | ✅ | ❌ | ❌ | Create new office branches |
| `departments:create` | ✅ | ✅ | ❌ | Create departments |
| `financial_year:create` | ✅ | ❌ | ❌ | Initialize new financial years |
| `darta:create` | ✅ | ✅ | ✅ | Register incoming Darta |
| `darta:forward` | ✅ | ✅ | ✅ | Forward Darta document |
| `chalan:create` | ✅ | ✅ | ✅ | Issue outgoing Chalan |
| `chalan:forward` | ✅ | ✅ | ✅ | Forward Chalan document |
| `logs:view` | ✅ | ✅ | ❌ | View audit and system logs |
| `document:download` | ✅ | ✅ | ✅ | Download document attachments |

---

## 📄 License
This project is licensed under the terms of the GNU General Public License v3.0 ([LICENSE](LICENSE)).