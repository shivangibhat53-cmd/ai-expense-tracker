from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.deps import get_db
from app.api.deps import get_current_user

from app.models.user import User

from app.schemas.analytics import (DashboardSummaryResponse,CategoryBreakdownResponse,
                                   MonthlyTrendResponse,BudgetStatusResponse,RecentTransactionResponse)
from app.services.analytics_service import (
    get_dashboard_summary,get_category_breakdown,
    get_monthly_trend,get_budget_status,get_recent_transactions
)

router = APIRouter(prefix = "/analytics", tags = ["Analytics"])

@router.get("/dashboard_summary", response_model= DashboardSummaryResponse)
def dashboard_summary(db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return get_dashboard_summary(db, current_user.id)

@router.get("/category-breakdown", response_model= List[CategoryBreakdownResponse])
def category_breakdown(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return get_category_breakdown(db,current_user.id)

@router.get("/monthly-trend", response_model=List[MonthlyTrendResponse])
def monthly_trend(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return get_monthly_trend(db,current_user.id)

@router.get("/budget-status",response_model=List[BudgetStatusResponse])
def budget_status(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return get_budget_status(db,current_user.id)

@router.get("/recent-transactions",response_model=List[RecentTransactionResponse])
def recent_transactions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_recent_transactions(
        db=db,
        user_id=current_user.id,
        limit=limit
    )