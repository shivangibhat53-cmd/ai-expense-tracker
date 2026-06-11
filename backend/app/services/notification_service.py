from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from fastapi import HTTPException

from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.user import User
from app.models.category import Category
from app.models.notification import Notification
from app.services.email_service import (
    send_budget_warning_email,
    send_budget_exceeded_email
)

def create_notification(db: Session, user_id:int, message : str):
    notification = Notification(user_id = user_id, message = message)

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notifications(db:Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def mark_notification_read(db: Session, user_id: int, notification_id : int):
    notification = db.query(Notification).filter(Notification.user_id == user_id and Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    if notification:
        notification.is_read = True
    
    db.commit()
    db.refresh(notification)

    return notification
def check_budget_alerts(db:Session, user_id:int, category_id: int):
    budget = db.query(Budget).filter(Budget.user_id == user_id and Budget.category_id == category_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not budget:
        return
    spent = (
    db.query(func.sum(Transaction.amount))
    .filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.type == "expense",
        extract("month", Transaction.created_at) == budget.month,
        extract("year", Transaction.created_at) == budget.year
    )
    .scalar()
    )

    spent = spent or 0

    percentage = (spent/budget.amount)*100

    if 90 <= percentage <100 and not budget.warning_sent:
        create_notification(db,user_id,
        f"You have used {percentage:.0f}% of your {budget.category.name} budget.")
        send_budget_warning_email(user.email,budget.category.name,spent,budget.amount)

    if percentage >= 100 and not budget.exceeded_sent:
        create_notification(db,user_id,
        f"You exceeded your {budget.category.name} budget.")
        
        send_budget_exceeded_email(user.email,budget.category.name,spent,budget.amount)



