from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from notification_service import create_notification

def create_budget(db: Session, user_id : int, data):
    
    category = db.query(Category).filter(Category.id == data.category_id, Category.user_id == user_id).first()

    if not category:
        raise HTTPException(status_code = 404, detail = "Category not found")
    
    existing = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category_id == data.category_id,
        Budget.month == data.month,
        Budget.year == data.year
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists"
        )
    budget = Budget(
        amount=data.amount,
        month=data.month,
        year=data.year,
        user_id=user_id,
        category_id=data.category_id
    )

    db.add(budget)

    db.commit()

    db.refresh(budget)

    return budget

def budget_status(db: Session, user_id : int, month: int, year : int):

    budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.month == month, Budget.year == year).all()

    results = []

    for budget in budgets:
        spent = db.query(func.coalesce(func.sum(Transaction.amount),0)).filter(Transaction.user_id == user_id, Transaction.category_id == budget.category_id, Transaction.type == "expense",
                        func.extract("month", Transaction.created_at) == budget.month, func.extract("year", Transaction.created_at) == budget.year).scalar()
        
        if spent >= budget.amount:
            create_notification(db, user_id, f"Budget exceeded for category - {budget.category_id}")
        
        elif spent >= budget.amount * 0.9:
            create_notification(db, user_id, f"Warning 90% budget used for category - {budget.category_id}")
            
        remaining = budget.amount - spent


        results.append({"category_id" : budget.category_id, "budget" : budget.amount, "spent" : spent, "remaining" : remaining, "overspent" : spent > budget.amount})

    return results