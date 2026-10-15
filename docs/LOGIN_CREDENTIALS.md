# Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
# Complete Directory of Available Login Credentials & System Access Keys

> **Confidentiality Notice:** This document lists initial, seeded, and testing credentials for the Nepal Telecom Darta-Chalan Digitization System. Change default passwords immediately upon deploying to a production network.

---

## 1. Web Portal User Credentials

To log in, navigate to **`http://localhost:3000`** (or your server's intranet IP `http://<SERVER_IP>:3000`).

### ⚠️ Crucial Login Requirement:
The portal enforces **Two-Factor Role Validation**. You **must** select the matching **User Role** from the dropdown menu on the login screen, or the system will reject the request with `Role mismatch`.

---

### A. Primary Production Administrator (Default Seeded Account)

This account is automatically provisioned during database initialization via `backend/scripts/seed.py`:

| Parameter | Value |
| :--- | :--- |
| **Email Address** | `admin@ntc.net.np` |
| **Password** | `Admin@123456` |
| **Role in Dropdown** | **`System Administrator`** (`SYSTEM_ADMIN`) |
| **Full Name** | System Admin |
| **Assigned Office** | NTC Central Office (ID: `1`) |
| **Assigned Department** | Administration Department (ID: `1`) |
| **Account Status** | Active (`is_disabled: false`) |
| **Capabilities** | Unrestricted access across all branches, users, master data, logs, and registers |

---

### B. Standard Test & Development Accounts (Automated Test Suite)

These accounts are used by the test fixtures in `tests/conftest.py` and can be provisioned in local/staging environments:

#### 1. Test System Administrator
| Parameter | Value |
| :--- | :--- |
| **Email Address** | `admin.test@ntc.net.np` |
| **Password** | `Secret123!` |
| **Role in Dropdown** | **`System Administrator`** (`SYSTEM_ADMIN`) |
| **Full Name** | Admin Test |
| **Office** | Central Office / Test Office |

#### 2. Test Staff Officer
| Parameter | Value |
| :--- | :--- |
| **Email Address** | `staff.test@ntc.net.np` |
| **Password** | `Secret123!` |
| **Role in Dropdown** | **`Staff Officer`** (`STAFF`) |
| **Full Name** | Staff Test |
| **Office** | Patan Branch / Test Office |
| **Capabilities** | Register incoming Darta, dispatch Chalan, forward documents, perform OCR searches |

---

## 2. Recommended Account Matrix for Office Deployment

When setting up a new branch or department, administrators should provision accounts following this standardized naming convention:

| Role Type | Recommended Email Pattern | Role in Dropdown | Typical Assignment |
| :--- | :--- | :--- | :--- |
| **Office Administrator** | `admin.<branch>@ntc.net.np`<br>*(e.g., `admin.patan@ntc.net.np`)* | `Office Administrator` | Branch Chief / Administrative Officer |
| **Intake / Front Desk Staff** | `reception.<branch>@ntc.net.np`<br>*(e.g., `reception.central@ntc.net.np`)* | `Staff Officer` | Front-desk operator scanning paper letters |
| **Dispatch / Chalan Staff** | `chalan.<dept>@ntc.net.np`<br>*(e.g., `chalan.billing@ntc.net.np`)* | `Staff Officer` | Department clerk issuing outgoing letters |
| **Department Head / Officer** | `<firstname>.<initial>@ntc.net.np`<br>*(e.g., `ramesh.k@ntc.net.np`)* | `Staff Officer` | Designated action officer reviewing documents |

---

## 3. Database & Infrastructure Credentials

These credentials are used by Docker services and system administrators to manage the PostgreSQL database:

| Component | Parameter | Configuration Value |
| :--- | :--- | :--- |
| **Database Engine** | PostgreSQL | Version 16 (Alpine) |
| **Database Name** | `POSTGRES_DB` | `darta_chalan_db` |
| **Database Superuser** | `POSTGRES_USER` | `ntc_admin` |
| **Database Password** | `POSTGRES_PASSWORD` | `ntc_secure_password_2081` |
| **Internal Docker Port** | Internal Port | `5432` |
| **Host Machine Port** | External Port | `5433` *(mapped to prevent conflict with local Postgres)* |
| **Full Connection URI** | SQLAlchemy URL | `postgresql+psycopg2://ntc_admin:ntc_secure_password_2081@localhost:5433/darta_chalan_db` |
| **Docker Container Name** | Container | `ntc_digitization_db` |

### Direct Database CLI Login Command:
```bash
# Connect to PostgreSQL directly inside the running container:
docker exec -it ntc_digitization_db psql -U ntc_admin -d darta_chalan_db
```

---

## 4. Inbound SMTP Hardware Scanner Socket Access

Network Multi-Function Printers (MFPs) and scanner daemons connect to the inbound mail socket using these parameters:

| Parameter | Configuration Value |
| :--- | :--- |
| **Protocol** | RFC 5321 ESMTP |
| **Host / Bind Address** | `0.0.0.0` (All network interfaces) |
| **Listening Port** | `1025` (Default) or `25` (Production) |
| **Authentication** | None (Anonymous intranet submission allowed) |
| **Allowed Recipient Domains** | `@ntc.net.np`, `@gov.np` |
| **Max Message Size** | 25 MB |
| **Default Target Office** | Office ID `1` (NTC Central Office) |

### Test Hardware Scanner Addresses:
- **Canon imageRUNNER Sender:** `scanner.canon@ntc.net.np`
- **Ministry Directive Sender:** `ministry.it@gov.np`
- **Branch Scanner Sender:** `scanner.branch@ntc.net.np`

---

## 5. Local Windows Hardware Scanner Bridge

The local desktop scanner bridge daemon connects directly to Windows USB scanners:

| Parameter | Value |
| :--- | :--- |
| **Service Name** | Windows Canon Scanner Bridge |
| **Local URL** | `http://127.0.0.1:8080` |
| **Health Check** | `http://127.0.0.1:8080/health` |
| **Device Listing** | `http://127.0.0.1:8080/devices` |
| **Scan Trigger Endpoint**| `POST http://127.0.0.1:8080/scan` |
| **Authentication** | Open CORS for local workstation browser session |

---

## 6. How to Reset a Forgotten Administrator Password

If the primary administrator password is forgotten or compromised, follow this procedure to reset it directly in PostgreSQL:

1. Open PowerShell / Command Prompt on the server host.
2. Generate a new Bcrypt password hash using Python:
   ```powershell
   python -c "from backend.app.core.security import hash_password; print(hash_password('NewAdminPass@2081'))"
   ```
   *(Suppose the output hash is `$2b$12$...`)*.
3. Update the database table directly:
   ```powershell
   docker exec -it ntc_digitization_db psql -U ntc_admin -d darta_chalan_db -c "UPDATE users SET password = '<PASTE_NEW_HASH_HERE>' WHERE email = 'admin@ntc.net.np';"
   ```
4. Alternatively, rerun the seeding script:
   ```powershell
   docker exec -it ntc_digitization_backend python backend/scripts/seed.py
   ```
5. Log in with the updated password and select `System Administrator` in the role dropdown.

---
*Document Version: 1.0.0 | Nepal Telecom Corporation IT Division*
