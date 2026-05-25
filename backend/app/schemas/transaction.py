from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class TransactionBase(BaseModel):
    amount : float
    type : str
    description: Optional[str] = None
    category_id : int


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount : Optional[float] = None
    type : Optional[str] = None
    description : Optional[str] = None
    category_id : Optional[int] = None


class TransactionResponse(TransactionBase):
    id : int
    user_id : int
    created_at : datetime

    class Config:
        from_attributes = True