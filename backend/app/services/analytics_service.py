from sqlalchemy.orm import Session
from sqlalchemy import func,case,extract

from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from datetime import datetime, timezone, timedelta

one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)

def get_dashboard_summary(
    db: Session,
    user_id: int
):
    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "income"
        )
        .scalar()
    )

    expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense"
        )
        .scalar()
    )

    transaction_count = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .count()
    )

    categories_count = (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .count()
    )

    active_budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id)
        .count()
    )

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense,
        "transaction_count": transaction_count,
        "categories_count": categories_count,
        "active_budgets": active_budgets
    }

def get_category_breakdown(db:Session, user_id:int):
    results = (db.query(
        Category.name, func.sum(Transaction.amount).label("total")).join
        (Transaction, Transaction.user_id == user_id)
        .filter(Transaction.user_id == user_id,Transaction.type == "expense")
        .group_by(Category.name).order_by(func.sum(Transaction.amount).desc()).all())

    return [{
        "category" : row.name,
        "amount"    : row.total
        }
     
     for row in results]

def get_monthly_trend(db:Session, user_id : int):
    results = (db.query(func.to_char(Transaction.created_at, "YYYY-MM").label("month"),
                        func.sum(case((Transaction.type == "income", Transaction.amount),else_ = 0)).label("income"),
                        func.sum(case((Transaction.type == "expense", Transaction.amount), else_= 0)).label("expense"))
                        .filter(Transaction.user_id == user_id,Transaction.created_at >= one_year_ago).group_by("month").order_by("month").all())
    
    return [
        {
            "month" : row.month,
            "income": float(row.income or 0),
            "expense": float(row.expense or 0),
            "savings" : row.expense - row.income
        }
        for row in results
    ]

def get_budget_status(
    db: Session,
    user_id: int
):

    results = (
        db.query(
            Budget.id,
            Budget.amount.label("budget_amount"),
            Budget.month,
            Budget.year,
            Category.name.label("category_name"),

            func.coalesce(
                func.sum(Transaction.amount),
                0
            ).label("spent")
        )
        .join(
            Category,
            Category.id == Budget.category_id
        )
        .outerjoin(
            Transaction,
            (
                (Transaction.category_id == Budget.category_id)
                &
                (Transaction.user_id == Budget.user_id)
                &
                (Transaction.type == "expense")
                &
                (
                    extract("month", Transaction.created_at)
                    == Budget.month
                )
                &
                (
                    extract("year", Transaction.created_at)
                    == Budget.year
                )
            )
        )
        .filter(
            Budget.user_id == user_id
        )
        .group_by(
            Budget.id,
            Budget.amount,
            Budget.month,
            Budget.year,
            Category.name
        )
        .all()
    )

    response = []

    for row in results:

        percentage = (
            row.spent / row.budget_amount * 100
        ) if row.budget_amount else 0

        remaining = row.budget_amount - row.spent

        if percentage >= 100:
            status = "exceeded"
        elif percentage >= 90:
            status = "warning"
        else:
            status = "healthy"

        response.append(
            {
                "category": row.category_name,
                "budget": float(row.budget_amount),
                "spent": float(row.spent),
                "remaining": float(remaining),
                "percentage": round(percentage, 2),
                "status": status,
                "month": str(row.month),
                "year": str(row.year)
            }
        )

    return response

def get_recent_transactions(
    db: Session,
    user_id: int,
    limit: int = 10
):
    transactions = (
        db.query(
            Transaction.id,
            Transaction.amount,
            Transaction.type,
            Transaction.description,
            Transaction.created_at,
            Category.name.label("category")
        )
        .join(
            Category,
            Category.id == Transaction.category_id
        )
        .filter(
            Transaction.user_id == user_id
        )
        .order_by(
            Transaction.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": tx.id,
            "amount": float(tx.amount),
            "type": tx.type,
            "category": tx.category,
            "description": tx.description,
            "created_at": tx.created_at
            
        }
        for tx in transactions
    ]