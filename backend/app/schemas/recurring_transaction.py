from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class RecurringTransactionResponse(BaseModel):
    merchant: str
    frequency: str
    occurrences: int
    average_amount: float
    confidence: float
    next_expected_date: datetime

class RecurringStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MISSED = "MISSED"
    CHURNED = "CHURNED"
    PAUSED = "PAUSED"

    class Config:
        from_attributes = True