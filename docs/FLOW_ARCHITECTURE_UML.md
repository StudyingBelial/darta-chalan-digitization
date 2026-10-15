# Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
# Flow Architecture & UML Diagram Specification

> **Purpose:** This document specifies the comprehensive flow architecture, data pipelines, sequence diagrams, state machines, and entity-relationship models for the Nepal Telecom Darta-Chalan Digitization Platform.
> **Compatibility:** Formatted in standard **Mermaid** and **PlantUML** code blocks, ready for instant rendering in Claude, ChatGPT, draw.io, PlantText, GitHub, or Mermaid Live Editor.

---

## Table of Contents
1. [High-Level System Architecture (C4 Container Diagram)](#1-high-level-system-architecture-c4-container-diagram)
2. [Sequence Diagram: Inbound SMTP Hardware Scanner Pipeline](#2-sequence-diagram-inbound-smtp-hardware-scanner-pipeline)
3. [Sequence Diagram: USB Desktop Scanner & Windows Bridge Pipeline](#3-sequence-diagram-usb-desktop-scanner--windows-bridge-pipeline)
4. [Sequence Diagram: Sequential Darta Numbering & Registration Flow](#4-sequence-diagram-sequential-darta-numbering--registration-flow)
5. [Sequence Diagram: Chalan Outgoing Dispatch Flow](#5-sequence-diagram-chalan-outgoing-dispatch-flow)
6. [State Machine Diagram: Document Lifecycle & Forwarding](#6-state-machine-diagram-document-lifecycle--forwarding)
7. [Sequence Diagram: Authentication & RBAC Permission Enforcement](#7-sequence-diagram-authentication--rbac-permission-enforcement)
8. [Entity Relationship Diagram (ERD) / UML Database Schema](#8-entity-relationship-diagram-erd--uml-database-schema)
9. [Instructions for Rendering with Claude / Diagram Tools](#9-instructions-for-rendering-with-claude--diagram-tools)

---

## 1. High-Level System Architecture (C4 Container Diagram)

```mermaid
graph TB
    subgraph Clients["User & Hardware Clients"]
        StaffBrowser["Staff Web Browser<br/>(Chrome/Edge/Firefox)"]
        AdminBrowser["Admin Web Browser<br/>(Management Portal)"]
        CanonMFP["Canon imageRUNNER / MFP<br/>(Network Scan-to-Email)"]
        USBScanner["Canon USB Scanner<br/>(DR-C225 / CanoScan LiDE)"]
    end

    subgraph Workstation["Operator Workstation"]
        WinBridge["Windows Scanner Bridge<br/>(Python WIA/TWAIN Port 8080)"]
    end

    subgraph HostSystem["Docker Containerized Platform"]
        subgraph WebReverseProxy["Reverse Proxy & Static Web Server"]
            NginxServer["Nginx (Port 80/443 / 3000)<br/>- React 18 SPA Build<br/>- Rate Limiting & SSL/TLS<br/>- Gzip Compression"]
        end

        subgraph ApplicationServer["Backend Application Server"]
            FastAPIServer["FastAPI REST Engine (Port 8000)<br/>- Controllers & Routers<br/>- Pydantic v2 DTOs<br/>- JWT & RBAC Engine"]
            SMTPServer["Inbound RFC 5321 ESMTP Service (Port 1025)<br/>- Network Socket Listener<br/>- MIME Attachment Extractor<br/>- Telemetry & Queue Ingestion"]
            OCRWorker["OCR & Parsing Engine<br/>- Tesseract Optical Recognition<br/>- Heuristic Field Parser<br/>- Confidence Scoring Matrix"]
            DateService["Nepali DateTime Engine<br/>- Bikram Sambat (B.S.) Conversion<br/>- Fiscal Year Computation"]
        end

        subgraph StorageLayer["Data & Persistence Layer"]
            PostgreSQL["PostgreSQL 16 Alpine<br/>- ACID Transactions<br/>- Isolated Sequential Numbers<br/>- Audit Event Ledger"]
            FileStorage["Date-Partitioned Storage<br/>(/app/storage/uploads)<br/>- SHA-256 Checksums<br/>- PDF/TIFF Document Archive"]
        end
    end

    %% Connections
    StaffBrowser -->|HTTPS/HTTP| NginxServer
    AdminBrowser -->|HTTPS/HTTP| NginxServer
    USBScanner -->|USB Hardware Cable| WinBridge
    WinBridge -->|CORS REST Port 8080| StaffBrowser
    CanonMFP -->|Raw ESMTP Socket Port 1025| SMTPServer

    NginxServer -->|Reverse Proxy /api/v1| FastAPIServer
    SMTPServer -->|Ingest Inbound Stream| FastAPIServer
    FastAPIServer -->|Trigger Text Extraction| OCRWorker
    FastAPIServer -->|Compute B.S. & FY| DateService
    FastAPIServer -->|Read/Write Records| PostgreSQL
    FastAPIServer -->|Store & Checksum Files| FileStorage
    SMTPServer -->|Save Attachments| FileStorage
```

---

## 2. Sequence Diagram: Inbound SMTP Hardware Scanner Pipeline

This sequence illustrates the end-to-end zero-click document intake from physical Canon network printers into the system:

```mermaid
sequenceDiagram
    autonumber
    actor Clerk as Office Operator
    participant MFP as Canon imageRUNNER MFP
    participant SMTP as SMTPServerService (Port 1025)
    participant Inbound as InboundService
    participant Storage as StorageService (SHA-256)
    participant OCR as OCRService (Tesseract)
    participant Parser as HeuristicDocumentParser
    participant DB as PostgreSQL Database
    participant UI as Inbound Queue Web UI

    Clerk->>MFP: Place paper document & press "Scan to Email"
    MFP->>SMTP: Connect TCP socket (RFC 5321 HELO/EHLO)
    SMTP-->>MFP: 250 ntc-darta-scanner.local Ready
    MFP->>SMTP: MAIL FROM: <scanner.canon@ntc.net.np>
    SMTP-->>MFP: 250 2.1.0 Sender OK
    MFP->>SMTP: RCPT TO: <intake@ntc.net.np>
    SMTP-->>MFP: 250 2.1.5 Recipient OK (Domain Verified)
    MFP->>SMTP: DATA (Stream multipart/mixed MIME & PDF payload)
    SMTP-->>MFP: 250 2.0.0 Message Accepted
    MFP->>SMTP: QUIT (Socket closed cleanly)

    critical Async Background Worker Ingestion
        SMTP->>SMTP: Inspect MIME headers & identify CANON_SCANNER signature
        SMTP->>Inbound: receive_inbound_document(file_bytes, source)
        Inbound->>Storage: save_file(file_bytes)
        Storage->>Storage: Compute SHA-256 checksum & store to /uploads/inbound/
        Storage-->>Inbound: file_path, sha256_hash
        Inbound->>OCR: extract_text(file_path)
        OCR-->>Inbound: raw_ocr_text (English + Devanagari)
        Inbound->>Parser: parse_text(raw_ocr_text, metadata)
        Parser->>Parser: Extract sender, email, topic, dates, reference numbers
        Parser->>Parser: Compute weighted confidence score (0.0 to 1.0)
        Parser-->>Inbound: candidate_fields, confidence_score, status
        Inbound->>DB: INSERT INTO inbound_documents (status: PENDING_REVIEW)
        Inbound->>DB: INSERT INTO notifications (target: STAFF)
    end

    UI->>Inbound: Poll /inbound/ (Badge alert triggers)
    Clerk->>UI: Review scanned document preview & auto-parsed candidate fields
    Clerk->>UI: Click "Convert to Official Darta"
    UI->>Inbound: POST /inbound/{id}/convert-darta
    Inbound->>DB: Generate sequential Darta ID & INSERT INTO darta
    Inbound->>DB: UPDATE inbound_documents SET status = 'CONVERTED_TO_DARTA'
    UI-->>Clerk: Display confirmed Darta registration record
```

---

## 3. Sequence Diagram: USB Desktop Scanner & Windows Bridge Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Receptionist
    participant Browser as React Web Client
    participant Bridge as Windows Scanner Bridge (Port 8080)
    participant WIA as Windows WIA / Canon Driver
    participant Backend as FastAPI /inbound/parse-file
    participant OCR as Tesseract OCR Engine

    Operator->>Browser: Click "Scan via Canon" on Darta Page
    Browser->>Bridge: GET http://127.0.0.1:8080/health
    Bridge-->>Browser: 200 OK (Device: Canon imageFORMULA DR-C225 detected)
    Operator->>Browser: Select ADF, 300 DPI, Auto-Deskew & Click "Start Scan"
    Browser->>Bridge: POST http://127.0.0.1:8080/scan {dpi: 300, source: 'ADF'}
    Bridge->>WIA: Trigger physical hardware page pull
    WIA-->>Bridge: Raw uncompressed bitmap stream
    Bridge->>Bridge: Apply contrast enhancement & deskew algorithm
    Bridge-->>Browser: Return compiled PDF/JPEG byte array
    Browser->>Browser: Display thumbnail gallery (rotate, delete blank pages)
    Operator->>Browser: Click "Accept & Transfer to Intake"
    Browser->>Backend: POST /api/v1/inbound/parse-file (Multipart Form)
    Backend->>OCR: Run high-accuracy Tesseract OCR
    OCR-->>Backend: Extracted text
    Backend-->>Browser: Return parsed candidate fields with confidence scores
    Browser-->>Operator: Display form with pre-filled sender, subject, and date
```

---

## 4. Sequence Diagram: Sequential Darta Numbering & Registration Flow

This diagram illustrates how sequential Darta numbers are strictly generated without race conditions, isolated per branch office and financial year:

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Staff Officer
    participant Controller as DartaController
    participant Workflow as DocumentWorkflowService
    participant DateEng as DateService
    participant Seq as SequenceService
    participant OCR as OCRService
    participant Storage as StorageService
    participant DB as PostgreSQL (Session)
    participant Audit as AuditLogService

    Staff->>Controller: POST /api/v1/darta (FormData + Document File)
    Controller->>Workflow: create_darta(current_user, darta_data, file)
    Workflow->>Workflow: Check permission (darta:create)
    Workflow->>Storage: upload_file(file, category="darta")
    Storage-->>Workflow: file_path, sha256_hash

    opt Darta Date provided in Gregorian A.D.
        Workflow->>DateEng: ad_to_bs(darta_date)
        DateEng-->>Workflow: darta_date_bs (e.g. 2081-06-25)
    end

    opt Financial Year not specified
        Workflow->>DateEng: get_nepali_fiscal_year()
        DateEng-->>Workflow: current_fy (e.g. "2081/82")
    end

    critical Database Sequence Transaction
        Workflow->>Seq: generate_next_darta_id(db, office_id, financial_year_id)
        Seq->>DB: SELECT COALESCE(MAX(darta_id), 0) + 1 FROM darta WHERE receiver_office = :office AND financial_year = :fy FOR UPDATE
        DB-->>Seq: next_darta_id (e.g. 104)
        Seq-->>Workflow: next_darta_id
    end

    Workflow->>OCR: extract_text(file_path)
    OCR-->>Workflow: extracted_ocr_text
    Workflow->>DB: INSERT INTO darta (darta_id, topic, sender, file_path, ocr_text, ...)
    DB-->>Workflow: Darta Record #104
    Workflow->>Audit: log_user_action("Created Darta entry #104")
    Audit->>DB: INSERT INTO logs (user_id, action, timestamp)
    Workflow-->>Controller: DartaResponse
    Controller-->>Staff: 201 Created (Darta #104 Confirmed)
```

---

## 5. Sequence Diagram: Chalan Outgoing Dispatch Flow

```mermaid
sequenceDiagram
    autonumber
    actor Clerk as Dispatch Clerk
    participant ChalanCtrl as ChalanController
    participant Workflow as DocumentWorkflowService
    participant Seq as SequenceService
    participant DB as PostgreSQL
    participant Audit as AuditLogService

    Clerk->>ChalanCtrl: POST /api/v1/chalan (Receiver, Topic, File, Office)
    ChalanCtrl->>Workflow: create_chalan(user, chalan_data, file)
    Workflow->>Workflow: Verify permission (chalan:create)
    Workflow->>Seq: generate_next_chalan_id(db, sender_office_id)
    Seq->>DB: SELECT COALESCE(MAX(chalan_id), 0) + 1 FROM chalan WHERE sender_office = :office FOR UPDATE
    DB-->>Seq: next_chalan_id (e.g. 452)
    Workflow->>DB: INSERT INTO chalan (chalan_id: 452, status: 'REGISTERED')
    Workflow->>Audit: log_user_action("Issued Chalan dispatch #452")
    Audit->>DB: INSERT INTO logs
    Workflow-->>ChalanCtrl: ChalanResponse
    ChalanCtrl-->>Clerk: Official Chalan Dispatch Issued (#452)
```

---

## 6. State Machine Diagram: Document Lifecycle & Forwarding

```mermaid
stateDiagram-v2
    [*] --> INBOUND_RECEIVED : Scanned via MFP / Direct Upload
    
    state INBOUND_RECEIVED {
        [*] --> PENDING_OCR
        PENDING_OCR --> PARSING_FIELDS : Tesseract Extracted Text
        PARSING_FIELDS --> PENDING_REVIEW : Confidence Calculated
    }

    PENDING_REVIEW --> REGISTERED : Staff Reviews & Converts to Darta
    PENDING_REVIEW --> DISMISSED : Junk / Duplicate Filtered

    state OFFICIAL_REGISTER {
        [*] --> REGISTERED : Auto Sequence Number Assigned
        REGISTERED --> FORWARDED : Routed to Dept / Officer
        FORWARDED --> UNDER_REVIEW : Recipient Department Opens
        UNDER_REVIEW --> ACTION_TAKEN : Response Letter / Decision Made
        ACTION_TAKEN --> COMPLETED : Sign-off Completed
        COMPLETED --> ARCHIVED : Fiscal Year Close / Retained
        FORWARDED --> FORWARDED : Re-routed to Secondary Branch
    }

    ARCHIVED --> [*]
```

---

## 7. Sequence Diagram: Authentication & RBAC Permission Enforcement

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Operator
    participant Client as React AuthContext
    participant AuthAPI as /api/v1/auth/login
    participant AuthSvc as AuthenticationService
    participant Security as Core Security (Bcrypt/JWT)
    participant ProtectRoute as Protected API Route (/darta)
    participant Dep as Dependencies (get_current_user & has_permission)

    User->>Client: Enter Email, Password, and Select Role Type (e.g. STAFF)
    Client->>AuthAPI: POST /api/v1/auth/login {email, password, user_type}
    AuthAPI->>AuthSvc: authenticate_user(login_data)
    AuthSvc->>AuthSvc: Verify user exists & is not disabled
    AuthSvc->>Security: verify_password(plain_password, hashed_password)
    Security-->>AuthSvc: Password Valid
    AuthSvc->>AuthSvc: Validate user.user_type == login_data.user_type
    Note over AuthSvc: Rejects request if Role Mismatch detected!
    AuthSvc->>Security: create_access_token({"sub": user.id})
    AuthSvc->>Security: create_refresh_token(user.id)
    Security-->>AuthSvc: access_token (120m), refresh_token (24h)
    AuthSvc-->>Client: {access_token, refresh_token, user_profile}
    Client->>Client: Store access_token in memory & localStorage

    Note over Client,ProtectRoute: Authenticated Session API Call
    Client->>ProtectRoute: GET /api/v1/darta (Authorization: Bearer <token>)
    ProtectRoute->>Dep: get_current_user(token)
    Dep->>Security: decode_jwt_token(token)
    Security-->>Dep: user_id
    Dep-->>ProtectRoute: Current Active User
    ProtectRoute->>Dep: has_permission(user, PERMISSIONS.DARTA_SEARCH)
    alt Has Permission
        Dep-->>ProtectRoute: True
        ProtectRoute-->>Client: 200 OK (Darta Records List)
    else Missing Permission
        Dep-->>ProtectRoute: False
        ProtectRoute-->>Client: 403 Forbidden ("Permission Denied")
    end
```

---

## 8. Entity Relationship Diagram (ERD) / UML Database Schema

```mermaid
erDiagram
    Offices ||--o{ Users : "employs"
    Offices ||--o{ Departments : "houses"
    Offices ||--o{ Officers : "contains"
    Offices ||--o{ Darta : "receives"
    Offices ||--o{ Chalan : "dispatches"
    Offices ||--o{ InboundDocument : "targets"
    Offices ||--o{ DocumentForwarding : "routes_to"

    Departments ||--o{ Officers : "allocates"
    Departments ||--o{ Darta : "manages"
    Departments ||--o{ Chalan : "originates"
    Departments ||--o{ DocumentForwarding : "assigned_to"

    FinancialYear ||--o{ Darta : "categorizes"
    FinancialYear ||--o{ Chalan : "categorizes"

    Users ||--o{ RefreshToken : "possesses"
    Users ||--o{ Logs : "triggers"
    Users ||--o{ Darta : "registers"
    Users ||--o{ Chalan : "registers"
    Users ||--o{ DocumentForwarding : "forwarded_by"

    Darta ||--o{ DocumentForwarding : "forwarding_trail"
    Chalan ||--o{ DocumentForwarding : "forwarding_trail"
    Darta ||--o{ Notification : "alerts_on"
    Chalan ||--o{ Notification : "alerts_on"
    InboundDocument ||--o{ Notification : "alerts_on"
    InboundDocument ||--o| Darta : "converts_to"
    InboundDocument ||--o| Chalan : "converts_to"

    Users {
        int id PK
        string full_name
        string email UK
        enum user_type "STAFF | OFFICE_ADMIN | SYSTEM_ADMIN"
        string password "Bcrypt Hash"
        int user_office FK
        boolean is_disabled
    }

    Offices {
        int id PK
        string name UK
        string location
    }

    Departments {
        int id PK
        string name UK
    }

    Officers {
        int id PK
        string name
        int department FK
        int office FK
    }

    FinancialYear {
        int id PK
        string financial_year UK "e.g. 2081/82"
    }

    Darta {
        int id PK
        int darta_id "Sequential Per FY/Office"
        int issued_by_user FK
        string sender
        string sender_email
        string sender_contact_number
        date darta_date "Gregorian A.D."
        string darta_date_bs "Bikram Sambat B.S."
        int financial_year FK
        string topic
        string file_name UK
        string file_path UK
        text extracted_ocr_text
        string status "REGISTERED | FORWARDED | etc."
        int receiver_office FK
        int receiver_department FK
        int receiver_officer FK
        timestamp timestamp
    }

    Chalan {
        int id PK
        int chalan_id "Sequential Per Office"
        int issued_by_user FK
        string sender_email
        string receiver
        string receiver_email
        string receiver_contact_number
        date chalan_date "Gregorian A.D."
        string chalan_date_bs "Bikram Sambat B.S."
        int financial_year FK
        string topic
        string file_name UK
        string file_path UK
        text extracted_ocr_text
        string status "REGISTERED | FORWARDED | etc."
        int sender_office FK
        int sender_department FK
        int sender_officer FK
        timestamp timestamp
    }

    InboundDocument {
        int id PK
        string source "CANON_SCANNER | SMTP_EMAIL | DIRECT_UPLOAD"
        string sender_email
        string sender_name
        string subject
        string file_name
        string file_path
        text extracted_ocr_text
        json parsed_data "Candidate Fields"
        float confidence_score "0.0 to 1.0"
        string parsing_status "PASSED_THRESHOLD | REQUIRES_REVIEW"
        string status "PENDING_REVIEW | CONVERTED_TO_DARTA | DISMISSED"
        int target_office_id FK
        int target_department_id FK
        int converted_darta_id FK
        int converted_chalan_id FK
        timestamp received_at
    }

    DocumentForwarding {
        int id PK
        string document_type "DARTA | CHALAN"
        int document_id
        int forwarded_by_user FK
        int forwarded_to_office FK
        int forwarded_to_department FK
        int forwarded_to_officer FK
        text remarks
        string status
        timestamp timestamp
    }

    Notification {
        int id PK
        int target_user_id FK
        int target_office_id FK
        string target_role
        string title
        text message
        string notification_type
        boolean is_read
        int darta_id FK
        int chalan_id FK
        int inbound_id FK
        string action_url
        timestamp created_at
    }

    Logs {
        int id PK
        int user_id FK
        enum log_type "INFO | WARNING | ERROR | CRITICAL"
        enum source "SYSTEM | USER"
        int office_id FK
        string message
        timestamp timestamp
    }

    RefreshToken {
        int id PK
        int user_id FK
        string token UK
        timestamp expires_at
        boolean is_revoked
        timestamp created_at
    }
```

---

## 9. Instructions for Rendering with Claude / Diagram Tools

### How to use this document with Claude:
You can paste any diagram block directly into Claude with prompts such as:
1. *"Render this Mermaid sequence diagram into a visual graphic or SVG."*
2. *"Convert this Mermaid ERD into a formal PlantUML class diagram for academic submission."*
3. *"Generate an interactive draw.io XML structure representing this architecture diagram."*

### How to use with PlantText or PlantUML CLI:
To convert any sequence diagram to PlantUML syntax, use the following template:
```plantuml
@startuml
skinparam handwritten false
skinparam monochrome false
skinparam shadowing true

actor Operator as "Office Clerk"
participant Scanner as "Canon imageRUNNER"
participant SMTP as "ESMTP Daemon (Port 1025)"
participant Backend as "FastAPI Inbound Engine"
database DB as "PostgreSQL 16"

Operator -> Scanner : Load document & Scan to Email
Scanner -> SMTP : RFC 5321 Delivery (PDF Attachment)
SMTP -> Backend : Parse MIME & Extract Text
Backend -> DB : Ingest into Inbound Documents
@enduml
```

---
*Architecture Specification Version: 1.0.0 | Nepal Telecom Corporation IT Division*
