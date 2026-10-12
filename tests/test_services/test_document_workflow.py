import pytest
from datetime import date
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.schemas import CreateDarta, CreateChalan
from backend.app.enums import DOCUMENT_STATUS, PERMISSIONS
from backend.app.core.exceptions import PermissionDeniedError

def test_create_darta_success(db_session, test_staff_user, test_office, test_department, test_officer, test_financial_year, tmp_path):
    # Create temp dummy file
    dummy_file = tmp_path / "test_doc.pdf"
    dummy_file.write_text("Test content")

    service = DocumentWorkflowService(db_session)
    darta_in = CreateDarta(
        sender="Ministry of Communication",
        sender_email="info@moc.gov.np",
        sender_contact_number="01-4200000",
        darta_date=date(2023, 8, 15),
        topic="Annual Telecom Report",
        receiver_office=test_office.id,
        receiver_department=test_department.id,
        receiver_officer=test_officer.id,
        financial_year=test_financial_year.id
    )

    darta = service.create_darta(
        user=test_staff_user,
        darta_data=darta_in,
        file_path=str(dummy_file)
    )

    assert darta.id is not None
    assert darta.darta_id == 1
    assert darta.sender == "Ministry of Communication"
    assert darta.darta_date_bs is not None
    assert darta.status == DOCUMENT_STATUS.REGISTERED.value

def test_create_chalan_success(db_session, test_staff_user, test_office, test_department, test_officer, tmp_path):
    dummy_file = tmp_path / "test_out.pdf"
    dummy_file.write_text("Outgoing content")

    service = DocumentWorkflowService(db_session)
    chalan_in = CreateChalan(
        receiver="Department of IT",
        receiver_email="doit@gov.np",
        sender_email="staff.test@ntc.net.np",
        chalan_date=date(2023, 8, 16),
        topic="Response to Query",
        sender_office=test_office.id,
        sender_department=test_department.id,
        sender_officer=test_officer.id
    )

    chalan = service.create_chalan(
        user=test_staff_user,
        chalan_data=chalan_in,
        file_path=str(dummy_file)
    )

    assert chalan.id is not None
    assert chalan.chalan_id == 1
    assert chalan.receiver == "Department of IT"
    assert chalan.chalan_date_bs is not None
    assert chalan.status == DOCUMENT_STATUS.REGISTERED.value
