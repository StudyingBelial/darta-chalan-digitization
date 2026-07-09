from pydantic import BaseModel
from typing import Optional, Literal

class FinancialYearCreate(BaseModel):
    financial_year: str

class FinancialYearUpdate(BaseModel):
    financial_year: str

class FilterFinancialYearSearch(BaseModel):
    id: Optional[int] = None
    financial_year: Optional[str] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

class FinancialYearResponse(BaseModel):
    id: int
    financial_year: str

    model_config = {"from_attributes": True}
