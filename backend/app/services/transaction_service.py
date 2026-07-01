from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException
from app.models.transaction import Transaction
from app.models.category import Category
from datetime import datetime
from app.services.notification_service import check_budget_alerts
from app.services.recurring_transaction import detect_recurring_transactions

def create_transaction(db: Session, user_id : int, data):
    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code = 404, detail = "Category not found")
    
    transaction = Transaction(
        amount = data.amount,
        type = data.type,
        description = data.description,
        category_id = data.category_id,
        user_id = user_id
    )



    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    detect_recurring_transactions(
    db,
    user_id,
    )

    print("CHECK_BUDGET_ALERTS CALLED")
    check_budget_alerts(
    db=db,
    user_id= user_id,
    category_id=transaction.category_id
    )


    return transaction

def get_transactions(db: Session, user_id : int,skip : int = 0, limit: int = 20, 
                     category_id: int| None = None, transaction_type : str| None = None, start_date : datetime| None= None, end_date: datetime |None = None):
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)

    if start_date:
        query = query.filter(Transaction.created_date >= start_date)

    if end_date:
        query = query.filter(Transaction.created_date <= end_date)

   
    return query.order_by(
        Transaction.created_at.desc()).offset(skip).limit(limit).all()


def get_transaction(db:Session, user_id : int, transaction_id : int):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user_id).first()

    if not transaction:
        raise HTTPException(status_code = 404, detail = "Transaction not found")
    return transaction

def get_transaction_summary(db:Session, user_id : int, start_date : datetime | None=None, end_date : datetime | None = None):
    query = db.query(
        func.coalesce(func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0)), 0).label("expense")
        ).filter(Transaction.user_id == user_id)

    if start_date:
        query = query.filter(Transaction.created_at >= start_date)

    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    result = query.first()

    income = result.income
    expense = result.expense

    return {
        "total_income" : income,
        "total_expense": expense,
        "net_balance"  : income - expense
    }

def category_breakdown(db:Session, user_id : int):
    results = db.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(Transaction.user_id == user_id, Transaction.type == "expense").group_by(Category.name).all()

    return [
        {
        "category" : r[0],
        "total" : r[1]
        }
        for r in results
    ]   


def update_transaction(db:Session, user_id : int, transaction_id : int, data):
    transaction = get_transaction(db,user_id,transaction_id)

    for key, values in data.dict(exclude_unset = True).items():
        setattr(transaction,key,values)

        db.commit()
        db.refresh(transaction)

    return transaction

def delete_transaction(db:Session,user_id : int, transaction_id :int):
    transaction = get_transaction (db, user_id, transaction_id)
    
    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted"}