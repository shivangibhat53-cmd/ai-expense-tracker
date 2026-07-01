from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.user import User

from app.schemas.recurring_transaction import (
    RecurringTransactionResponse, 
)

from app.services.recurring_transaction import (
    detect_recurring_transactions, get_recurring_transactions,
)

router = APIRouter(
    prefix="/recurring-transactions",
    tags=["Recurring Transactions"],
)


@router.get(
    "/",
    response_model=list[RecurringTransactionResponse],
)
def recurring_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Return stored recurring transactions
    return get_recurring_transactions(
        db=db,
        user_id=current_user.id,
    )