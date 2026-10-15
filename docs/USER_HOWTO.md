# Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
# User & Operator Manual (प्रयोगकर्ता हातेपुस्तिका)

> **Platform:** Darta-Chalan Digitization Portal (दर्ता-चलानी डिजिटल प्रणाली)  
> **Target Audience:** Administrative Staff, Desk Operators, Registration Clerks, Department Officers  
> **Scope:** Daily document registration, hardware scanning, OCR search, document forwarding, and dispatch

---

## Table of Contents
1. [Introduction to Darta & Chalan](#1-introduction-to-darta--chalan)
2. [Logging In to the System](#2-logging-in-to-the-system)
3. [Understanding Your Dashboard](#3-understanding-your-dashboard)
4. [Darta Workflow (दर्ता - Incoming Document Registration)](#4-darta-workflow-दर्ता---incoming-document-registration)
5. [Using the Canon & Hardware Document Scanner](#5-using-the-canon--hardware-document-scanner)
6. [Chalan Workflow (चलानी - Outgoing Document Dispatch)](#6-chalan-workflow-चलानी---outgoing-document-dispatch)
7. [Inbound Queue & AI-Assisted Document Intake](#7-inbound-queue--ai-assisted-document-intake)
8. [Document Forwarding & Routing History](#8-document-forwarding--routing-history)
9. [Advanced Search & OCR Full-Text Document Retrieval](#9-advanced-search--ocr-full-text-document-retrieval)
10. [Exporting Official Government Registers (दर्ता/चलानी किताब)](#10-exporting-official-government-registers-दर्ताचलानी-किताब)
11. [Managing Your User Profile & Password](#11-managing-your-user-profile--password)
12. [Frequently Asked Questions (FAQ)](#12-frequently-asked-questions-faq)

---

## 1. Introduction to Darta & Chalan

In government and enterprise administration across Nepal:
- **Darta (दर्ता - Incoming):** The legal registration of any formal letter, circular, tender, or memorandum received from external entities (ministries, vendors, customers, or other NTC branch offices).
- **Chalan (चलानी - Outgoing):** The official dispatch and recording of outgoing correspondence issued by Nepal Telecom to external organizations or between internal divisions.

This platform replaces physical, handwritten paper books with an automated, tamper-proof, digitized registry with search and scanning capabilities.

---

## 2. Logging In to the System

1. Open your web browser (Google Chrome, Microsoft Edge, or Mozilla Firefox).
2. Enter the portal address provided by your IT Administrator:
   - On the office intranet: `http://<SERVER_IP>:3000` (e.g. `http://192.168.1.31:3000` or `http://darta.ntc.net.np`)
   - On your local PC: `http://localhost:3000`

### ⚠️ IMPORTANT STEP: Role Selection
The login screen includes a **Select User Role** dropdown. You must select the role that matches your account:
- **Staff Officer (`STAFF`):** For general operators, intake clerks, and department officers.
- **Office Administrator (`OFFICE_ADMIN`):** For branch supervisors managing users and officers.
- **System Administrator (`SYSTEM_ADMIN`):** For central IT personnel.

```
+-------------------------------------------------------+
|  [Select User Role] -> Staff Officer / Admin          |
|  [Email Address]    -> your.name@ntc.net.np           |
|  [Password]         -> ••••••••••••                   |
|  [ Sign In to Portal ]                                |
+-------------------------------------------------------+
```

> **Note:** If you choose a role that does not match your assigned account, the system will return `Role mismatch`. Always verify your selected role.

---

## 3. Understanding Your Dashboard

Upon logging in, you are greeted by the **Real-Time Operational Dashboard**:
- **Metric Cards:**
  - **Total Darta Registered:** Lifetime incoming records for your office.
  - **Total Chalan Dispatched:** Lifetime outgoing records.
  - **Inbound Intake Queue:** Scanned documents awaiting staff verification.
  - **Today's Activity:** Registrations performed in the current business day.
- **Notification Drawer (Top-Right Bell):**
  - Instant badges showing documents forwarded to your department or newly received scanner dispatches.
- **Navigation Sidebar:**
  - **Dashboard:** Overview and metrics.
  - **Darta (Incoming):** Search, view, and register incoming letters.
  - **Chalan (Outgoing):** Search, view, and issue outgoing dispatches.
  - **Inbound Queue:** AI-parsed documents received from network scanners.
  - **Audit Logs / Master Data:** Accessible to Administrators.

---

## 4. Darta Workflow (दर्ता - Incoming Document Registration)

When an official letter arrives at your office:

### Step 1: Open Registration Modal
Navigate to **Darta (Incoming)** in the sidebar. You have two convenient methods:
- **Method A (Direct Hardware Scan):** Click **Scan via Canon**. This opens the hardware scanner modal to capture pages directly from your scanner feeder.
- **Method B (File Upload):** Click **+ New Darta Entry** or **Universal Document Intake** to upload an existing PDF, PNG, or JPG file.

### Step 2: Fill in Document Details
The system automatically populates the **Darta Registration Number** and computes the **Bikram Sambat (B.S.) date**:
- **Sender / Organization:** The organization or individual sending the letter (e.g., *Ministry of Communications & Information Technology*).
- **Sender Email Address:** The sender's official email (e.g., *info@mocit.gov.np*).
- **Sender Contact Number:** Phone number for tracking.
- **Topic / Subject (विषय):** Clear subject of the letter (e.g., *Broadband Infrastructure Expansion Guidelines*).
- **Darta Date (A.D. & B.S.):** Defaults to today's date. The Nepali Bikram Sambat date (e.g. `2081-06-25`) is generated automatically.
- **Financial Year:** Automatically selected for the current fiscal cycle (e.g., `2081/82`).
- **Designated Destination:**
  - **Receiver Department:** Select which division handles this letter (e.g., *IT Operations*, *Administration*).
  - **Receiver Officer:** Select the designated officer.

### Step 3: Attach the Scanned File & Submit
- Choose your PDF or image attachment (or use scanned pages from the hardware scanner).
- Click **Complete Registration**.
- The system:
  1. Assigns the next sequential Darta Number.
  2. Runs background OCR to extract all readable text.
  3. Secures the file with a cryptographic SHA-256 digital fingerprint.
  4. Stores the record in the permanent Darta Register.

---

## 5. Using the Canon & Hardware Document Scanner

The platform includes a dedicated **Canon & Hardware Scanner Interface** for high-speed scanning:

### How to Scan Physical Pages:
1. Load your paper documents into the scanner tray:
   - For multi-page documents, use the **Automatic Document Feeder (ADF)**.
   - For single-sheet or sensitive originals, place on the **Flatbed glass**.
2. Click **Scan via Canon** on the Darta page.
3. Configure your scan settings on the left sidebar:
   - **Device:** Select your connected scanner (e.g., *Canon imageFORMULA DR-C225* or *CanoScan LiDE 400*).
   - **Paper Source:** ADF or Flatbed.
   - **Resolution (DPI):** 300 DPI (Recommended for crisp OCR accuracy).
   - **Color Mode:** Color, Grayscale, or Black & White.
   - **Image Enhancements:** Enable **Auto-Deskew** (straightens crooked pages) and **Contrast Enhancement** (sharpens faint text).
4. Click **Start Hardware Scan**.
5. The scanned page thumbnails appear in the gallery:
   - Click any thumbnail to preview full resolution.
   - Use **Rotate Clockwise (90°)** or **Rotate Counter-Clockwise** if a page was fed upside down.
   - Delete any blank or duplicate pages with the **Trash** icon.
6. When satisfied, click **Accept & Transfer to Intake**. The scanned pages are automatically compiled into a clean PDF and forwarded to the registration form.

---

## 6. Chalan Workflow (चलानी - Outgoing Document Dispatch)

When issuing an official letter from Nepal Telecom to an outside organization:

1. Navigate to **Chalan (Outgoing)** in the sidebar.
2. Click **+ New Chalan Entry**.
3. Fill in the dispatch details:
   - **Receiver / Organization:** The destination entity (e.g., *Nepal Telecommunications Authority (NTA)*).
   - **Receiver Email Address:** Official destination email.
   - **Receiver Contact Number:** Phone number.
   - **Subject / Topic:** Subject of the outgoing letter.
   - **Sender Office & Department:** Your branch and department issuing the dispatch.
   - **Designated Sender Officer:** The signatory officer.
4. Upload the signed and stamped copy of the dispatch letter.
5. Click **Issue Chalan Dispatch**.
6. The system allocates the next official **Chalan Number**, records the timestamp, and creates the entry in the Chalan Register.

---

## 7. Inbound Queue & AI-Assisted Document Intake

If your office has a network multi-function printer (Canon imageRUNNER, HP, Ricoh, or Xerox) configured with Scan-to-Email, documents arrive automatically in the **Inbound Queue** without any manual file uploading!

### Reviewing Inbound Documents:
1. Navigate to **Inbound Queue** in the sidebar.
2. You will see a list of documents received via scanner or email.
3. Click **Review & Convert** on any inbound document.
4. The **Unified Document Intake Modal** opens:
   - The left pane displays a live preview of the scanned letter.
   - The right pane displays **Candidate Fields** extracted automatically by the OCR engine:
     - Detected Sender
     - Detected Email
     - Detected Subject / Topic
     - Detected Date
   - Each field displays a **Confidence Rating** (e.g. `95% Confidence - High Accuracy`).
5. Verify the extracted fields, make any minor corrections if needed, select the internal department to route the document to, and click **Convert to Official Darta**.
6. The document is instantly converted into a registered Darta record!

---

## 8. Document Forwarding & Routing History

Once a Darta or Chalan is registered, it frequently needs to be routed to other branches or officers for action.

### How to Forward a Document:
1. In the Darta or Chalan table, click the **Paper Plane icon (Forward)** on the desired record.
2. In the forwarding modal:
   - Select the **Target Office / Branch**.
   - Select the **Target Department**.
   - Select the **Designated Officer**.
   - Enter **Action Instructions / Remarks** (e.g., *For your immediate review and recommendation regarding fiber rollout*).
3. Click **Dispatch Forwarding**.
4. The system updates the document status to `FORWARDED`, logs the transfer in the audit trail, and sends an alert to the receiving department.

### Viewing Document Movement History:
- Click the **Eye icon** or **Timeline** on any document to see its complete visual movement chain:
  - Who registered the letter.
  - Every officer it was forwarded to, including timestamps and specific remarks.

---

## 9. Advanced Search & OCR Full-Text Document Retrieval

Finding historical letters is effortless using the multi-parameter search bar:

### Search Capabilities:
- **Registration Number:** Enter Darta or Chalan number.
- **Sender / Receiver Name:** Filter by organization name.
- **Subject / Topic:** Search keywords in the document title.
- **Bikram Sambat (B.S.) Date Range:** Filter from date (e.g., `2081-01-01`) to date (e.g., `2081-06-30`).
- **Fiscal Year:** View documents from a specific financial year (`2080/81`, `2081/82`).
- **OCR Full-Text Keyword Search:**
  - Type any word that appears **inside the body of the scanned paper letter**.
  - The system searches the indexed OCR text and returns the matching document even if the keyword is not in the subject!
  - Click the **OCR / Microchip icon** on any row to open the **OCR Inspector Modal** and copy the extracted raw text directly.

---

## 10. Exporting Official Government Registers (दर्ता/चलानी किताब)

For administrative audits, inspections, or offline archiving:
1. Navigate to **Darta** or **Chalan**.
2. Apply any desired filters (e.g., specific Fiscal Year or Date Range), or leave clear for all records.
3. Click **Export Register (CSV / Excel)**.
4. The system generates a formatted file adhering to official Nepalese government register columns:
   - Darta/Chalan Number
   - Date (A.D. & B.S.)
   - Fiscal Year
   - Sender & Receiver details
   - Subject
   - Status & Department routing
   - Document file reference

---

## 11. Managing Your User Profile & Password

1. Click your name in the top navigation bar and select **User Profile**.
2. Under **Change Password**:
   - Enter your **Current Password**.
   - Enter your **New Password** (minimum 8 characters, combining letters, numbers, and symbols).
   - Confirm your new password and click **Update Password**.
3. If you ever forget your password, contact your **Office Administrator** who can issue an immediate administrative password reset.

---

## 12. Frequently Asked Questions (FAQ)

### Q: Why did the system show "Role mismatch" during login?
**A:** You must select the role in the login dropdown that matches your account permissions (`STAFF`, `OFFICE_ADMIN`, or `SYSTEM_ADMIN`). Verify your role with your supervisor.

### Q: Can I edit a Darta record after submitting it?
**A:** Regular staff can view and forward documents. Only Administrators have permission to edit metadata once registered, preserving legal auditability.

### Q: What file formats are supported for document attachments?
**A:** PDF, PNG, JPG, JPEG, and TIFF up to 25 MB per document. PDF is strongly recommended for multi-page correspondence.

### Q: Can I search for documents using Nepali Bikram Sambat dates?
**A:** Yes! The search panel includes dedicated `From Date (B.S.)` and `To Date (B.S.)` fields (e.g., `2081-05-15`).

---
*Nepal Telecom Corporation — Connecting the Nation through Digital Excellence*
