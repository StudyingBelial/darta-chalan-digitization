from datetime import date, datetime
from backend.app.core.exceptions import InvalidBSDateError
from backend.app.core.logger import logger

try:
    import nepali_datetime
except ImportError:
    nepali_datetime = None

class DateService:
    @staticmethod
    def ad_to_bs(ad_date: date | datetime | None = None) -> str:
        """
        Convert Gregorian (A.D.) date to Bikram Sambat (B.S.) date string (YYYY-MM-DD).
        """
        if ad_date is None:
            ad_date = date.today()
        elif isinstance(ad_date, datetime):
            ad_date = ad_date.date()

        if nepali_datetime:
            try:
                bs_obj = nepali_datetime.date.from_datetime_date(ad_date)
                return bs_obj.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(f"nepali_datetime conversion failed for {ad_date}: {e}")

        # Fallback estimation (+56 years, +8 months, +15 days approx for display)
        year = ad_date.year + 57
        return f"{year:04d}-{ad_date.month:02d}-{ad_date.day:02d}"

    @staticmethod
    def bs_to_ad(bs_str: str) -> date:
        """
        Convert Bikram Sambat (B.S.) date string (YYYY-MM-DD) to Gregorian (A.D.) date.
        """
        try:
            parts = [int(p) for p in bs_str.strip().split("-")]
            if len(parts) != 3:
                raise ValueError("Format must be YYYY-MM-DD")
            year, month, day = parts
        except Exception as e:
            raise InvalidBSDateError(f"Invalid B.S. date format: {bs_str}. Expected YYYY-MM-DD. Error: {e}")

        if nepali_datetime:
            try:
                bs_obj = nepali_datetime.date(year, month, day)
                return bs_obj.to_datetime_date()
            except Exception as e:
                logger.warning(f"nepali_datetime bs_to_ad failed for {bs_str}: {e}")

        # Fallback estimation (-57 years)
        return date(max(year - 57, 1900), month, day)

    @staticmethod
    def get_nepali_fiscal_year(ad_date: date | None = None) -> str:
        """
        Determine Nepali Fiscal Year (e.g., '2080/81') for a given date.
        Nepali Fiscal Year starts on 1st Shrawan (approx July 16 / Month 4 in BS).
        """
        bs_str = DateService.ad_to_bs(ad_date)
        year, month, _ = [int(p) for p in bs_str.split("-")]
        
        # Shrawan is month 4 in BS
        if month >= 4:
            current_yr = year
            next_yr = (year + 1) % 100
        else:
            current_yr = year - 1
            next_yr = year % 100
            
        return f"{current_yr}/{next_yr:02d}"
