from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user

from app.models.user import User

from app.schemas.budget import(BudgetCreate, BudgetResponse)

import app.services.budget_service as service

router = APIRouter(prefix = "/budgets", tags = ["Budgets"])

@router.post("/", response_model = BudgetResponse)

def create_budget(data: BudgetCreate, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.create_budget(db,current_user.id, data)

@router.get("/status")
def get_budget_status(month: int, year: int, db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.budget_status(db, current_user.id, month, year)
