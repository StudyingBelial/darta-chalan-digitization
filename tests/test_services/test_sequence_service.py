from backend.app.services.sequence_service import SequenceService

def test_darta_sequence_generation(db_session, test_office, test_financial_year):
    seq1 = SequenceService.generate_next_darta_id(db_session, test_office.id, test_financial_year.id)
    assert seq1 == 1

def test_chalan_sequence_generation(db_session, test_office):
    seq1 = SequenceService.generate_next_chalan_id(db_session, test_office.id)
    assert seq1 == 1
