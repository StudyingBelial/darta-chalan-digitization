from datetime import date
from backend.app.services.date_service import DateService

def test_ad_to_bs_conversion():
    ad = date(2024, 1, 15)
    bs_str = DateService.ad_to_bs(ad)
    assert isinstance(bs_str, str)
    assert len(bs_str.split("-")) == 3

def test_nepali_fiscal_year_calculation():
    fy = DateService.get_nepali_fiscal_year(date(2024, 1, 15))
    assert "/" in fy
