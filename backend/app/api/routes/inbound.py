from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.schemas.inbound import (
    InboundDocumentResponse,
    InboundDocumentFilter,
    ConvertInboundToDarta,
    SimulateEmailRequest,
    ParsedCandidateFields,
    SMTPScannerStatusResponse,
    SMTPTestEmailRequest,
    SMTPToggleRequest
)
from backend.app.schemas.darta import DartaResponse
from backend.app.controllers.inbound import InboundController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/inbound", tags=["Inbound & Email Parsing"])

# ------------------------------------------------------------------------------
# Inbound SMTP Scanner & Hardware Ingestion Endpoints
# ------------------------------------------------------------------------------
@router.get("/smtp/status", response_model=SMTPScannerStatusResponse)
async def get_smtp_scanner_status(
    current_user: Users = Depends(get_current_user)
):
    """
    Get live status, telemetry metrics, and bind information for the Inbound SMTP Scanner.
    """
    return await InboundController.get_smtp_status(current_user)

@router.post("/smtp/test-send")
async def send_smtp_test_scan(
    payload: SMTPTestEmailRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    Dispatch a realistic test scanned document through the loopback SMTP scanner listener.
    Tests end-to-end socket reception, MIME attachment parsing, OCR, and notification dispatch.
    """
    return await InboundController.send_smtp_test_email(payload, current_user)

@router.post("/smtp/toggle", response_model=SMTPScannerStatusResponse)
async def toggle_smtp_scanner(
    payload: SMTPToggleRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    Dynamically start or stop the Inbound SMTP Scanner Service (Admin only).
    """
    return await InboundController.toggle_smtp_scanner(payload, current_user)

@router.get("", response_model=List[InboundDocumentResponse])
async def list_inbound_documents(
    filter_params: InboundDocumentFilter = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List inbound documents with filtering by status, source, and search term.
    """
    return await InboundController.list_inbound_documents(filter_params, current_user, db)

@router.get("/{inbound_id}", response_model=InboundDocumentResponse)
async def get_inbound_document(
    inbound_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information and current parsed candidate fields for an inbound document.
    """
    return await InboundController.get_inbound_document(inbound_id, current_user, db)

@router.post("/{inbound_id}/parse", response_model=InboundDocumentResponse)
async def parse_inbound_document(
    inbound_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger or re-run automatic document OCR and field extraction on an inbound document.
    """
    return await InboundController.parse_inbound_document(inbound_id, current_user, db)

@router.post("/parse-file", response_model=ParsedCandidateFields)
async def parse_uploaded_file(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Auto-parse an uploaded PDF/image or Canon scanned document on-the-fly.
    Returns candidate fields, confidence scores, and threshold pass/fail status.
    """
    return await InboundController.parse_uploaded_file(file, db)

@router.post("/{inbound_id}/convert-darta", response_model=DartaResponse)
async def convert_inbound_to_darta(
    inbound_id: int,
    payload: ConvertInboundToDarta,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convert a reviewed and verified inbound document into an official Darta register record.
    """
    return await InboundController.convert_inbound_to_darta(inbound_id, payload, current_user, db)

@router.post("/simulate-email", response_model=InboundDocumentResponse)
async def simulate_incoming_email(
    payload: SimulateEmailRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate incoming SMTP email with PDF attachment for testing and demonstrating
    the automated notification and high-threshold parsing lifecycle.
    """
    return await InboundController.simulate_incoming_email(payload, current_user, db)

@router.get("/{inbound_id}/download")
async def download_inbound_file(
    inbound_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download attached inbound document file.
    """
    return await InboundController.download_inbound_file(inbound_id, current_user, db)
