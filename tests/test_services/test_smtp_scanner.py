import pytest
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import socket
from contextlib import contextmanager

from backend.app.services.smtp_scanner import SMTPServerService, smtp_scanner_service
from backend.app.db.models.inbound_document import InboundDocument
from backend.app.db.models.notification import Notification
from backend.app.core.security import create_access_token

def get_free_port() -> int:
    """Find a dynamically available local port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def test_smtp_scanner_lifecycle():
    """Verify that SMTP service starts, reports status, and stops cleanly."""
    async def _run():
        scanner = SMTPServerService()
        test_port = get_free_port()
        
        started = await scanner.start(host="127.0.0.1", port=test_port)
        assert started is True
        assert scanner.is_running is True

        status = scanner.get_status()
        assert status["running"] is True
        assert status["port"] == test_port
        assert status["messages_processed"] == 0

        stopped = await scanner.stop()
        assert stopped is True
        assert scanner.is_running is False

    asyncio.run(_run())

def test_smtp_socket_esmtp_handshake():
    """Verify RFC 5321 ESMTP protocol commands with raw asyncio streams."""
    async def _run():
        scanner = SMTPServerService()
        test_port = get_free_port()
        await scanner.start(host="127.0.0.1", port=test_port)

        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", test_port)
            
            # Banner
            banner = await reader.readline()
            assert b"220" in banner

            # EHLO
            writer.write(b"EHLO client.test.ntc\r\n")
            await writer.drain()
            ehlo_resp = b""
            while True:
                line = await reader.readline()
                ehlo_resp += line
                if line.startswith(b"250 "):
                    break
            assert b"250" in ehlo_resp

            # MAIL FROM
            writer.write(b"MAIL FROM:<scanner@branch.ntc.net.np>\r\n")
            await writer.drain()
            mail_resp = await reader.readline()
            assert mail_resp.startswith(b"250")

            # RCPT TO
            writer.write(b"RCPT TO:<darta@ntc.net.np>\r\n")
            await writer.drain()
            rcpt_resp = await reader.readline()
            assert rcpt_resp.startswith(b"250")

            # DATA
            writer.write(b"DATA\r\n")
            await writer.drain()
            data_resp = await reader.readline()
            assert data_resp.startswith(b"354")

            # Send simple message body
            msg_body = (
                b"Subject: Test Scanner Dispatch\r\n"
                b"From: scanner@branch.ntc.net.np\r\n"
                b"To: darta@ntc.net.np\r\n"
                b"\r\n"
                b"Scanned test document text body.\r\n"
                b".\r\n"
            )
            writer.write(msg_body)
            await writer.drain()
            done_resp = await reader.readline()
            assert done_resp.startswith(b"250")

            # QUIT
            writer.write(b"QUIT\r\n")
            await writer.drain()
            quit_resp = await reader.readline()
            assert quit_resp.startswith(b"221")

            writer.close()
            await writer.wait_closed()
        finally:
            await scanner.stop()

    asyncio.run(_run())

def test_smtp_scanner_receives_mime_pdf_attachment(db_session, test_office):
    """
    Test real SMTP email transmission with PDF attachment and verify
    it gets ingested into InboundDocuments.
    """
    async def _run():
        scanner = SMTPServerService()
        test_port = get_free_port()
        scanner.default_office_id = test_office.id

        @contextmanager
        def _test_session():
            yield db_session

        scanner.session_factory = _test_session
        await scanner.start(host="127.0.0.1", port=test_port)

        try:
            # Build multipart MIME with attached PDF
            msg = MIMEMultipart()
            msg["From"] = "Canon imageRUNNER 2520 <canon.scanner@ntc.net.np>"
            msg["To"] = "darta@ntc.net.np"
            msg["Subject"] = "Scanned Directive on Network Upgrade 2081"
            msg["User-Agent"] = "Canon imageRUNNER ADVANCE Scan-to-Email"

            msg.attach(MIMEText("Scanned page from Canon imageRUNNER 2520.", "plain"))

            # Minimal valid PDF payload
            pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
            part = MIMEApplication(pdf_bytes, _subtype="pdf")
            part.add_header("Content-Disposition", "attachment", filename="canon_directive_2081.pdf")
            msg.attach(part)

            loop = asyncio.get_running_loop()
            def _send():
                with smtplib.SMTP("127.0.0.1", test_port, timeout=10) as s:
                    s.send_message(msg)

            await loop.run_in_executor(None, _send)
            await asyncio.sleep(0.5)

            assert scanner.messages_processed >= 1
            assert scanner.last_sender == "canon.scanner@ntc.net.np"
            assert "Directive" in scanner.last_subject

            # Verify DB document creation
            inbound_doc = db_session.query(InboundDocument).filter(
                InboundDocument.sender_email == "canon.scanner@ntc.net.np"
            ).first()
            assert inbound_doc is not None
            assert inbound_doc.source == "CANON_SCANNER"
            assert "canon_directive_2081.pdf" in inbound_doc.file_name

        finally:
            await scanner.stop()

    asyncio.run(_run())

def test_smtp_api_routes(client, test_admin_user):
    """Test REST API endpoints for SMTP scanner status and test-send."""
    token = create_access_token({"sub": str(test_admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /inbound/smtp/status
    res = client.get("/api/v1/inbound/smtp/status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "running" in data
    assert "port" in data
    assert "messages_processed" in data

    # 2. POST /inbound/smtp/toggle
    toggle_res = client.post("/api/v1/inbound/smtp/toggle", json={"enable": True}, headers=headers)
    assert toggle_res.status_code == 200
    toggle_data = toggle_res.json()
    assert toggle_data["running"] is True

    # 3. POST /inbound/smtp/test-send
    send_res = client.post(
        "/api/v1/inbound/smtp/test-send",
        json={
            "sender_email": "scanner.api@ntc.net.np",
            "sender_name": "API Test Scanner",
            "subject": "Automated Integration Test Scan",
            "file_name": "api_test_scan.pdf"
        },
        headers=headers
    )
    assert send_res.status_code == 200
    send_data = send_res.json()
    assert send_data["success"] is True

    # Check status again to verify processed counter incremented
    import time
    time.sleep(0.5)
    res2 = client.get("/api/v1/inbound/smtp/status", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["messages_processed"] >= 1
