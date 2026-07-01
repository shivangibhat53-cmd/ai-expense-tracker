from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RecurringTransactionResponse(BaseModel):
    merchant: str
    frequency: str
    occurrences: int
    average_amount: float
    confidence: float
    next_expected_date: datetime

    class Config:
        from_attributes = True