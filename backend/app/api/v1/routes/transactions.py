from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)


import app.services.transaction_service as service

router = APIRouter(prefix="/transactions",tags = ["Transactions"])


@router.post("/", response_model = TransactionResponse)
def create_transaction(
    data : TransactionCreate,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)

):
    return service.create_transaction(db,current_user.id, data)

@router.get("/", response_model = List[TransactionResponse])
def list_transactions(
    skip : int = 0,
    limit : int = 20,
    category_id : Optional[int] = None,
    transaction_type : Optional[str] = None,
    start_date:Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db : Session = Depends(get_db),
    current_user: User =  Depends(get_current_user)
):
    return service.get_transactions(db=db, user_id=current_user.id, skip=skip, limit = limit,category_id = category_id,transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/summary")
def transaction_summary(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return service.get_transaction_summary(
        db,
        current_user.id,
        start_date,
        end_date
    )

@router.get("/category-breakdown")
def category_analytics(db:Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.category_breakdown(db, current_user.id)


@router.get("/{transaction_id}", response_model = TransactionResponse)
def get_transaction(transaction_id : int, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.get_transaction(db, current_user.id, transaction_id)

@router.put("/{transaction_id}", response_model = TransactionResponse)
def update_transaction( transaction_id : int, data : TransactionUpdate, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.update_transaction(db, current_user.id, transaction_id, data)

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.delete_transaction(db, current_user.id, transaction_id)