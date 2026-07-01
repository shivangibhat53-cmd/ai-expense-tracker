import pytest
from datetime import datetime, timedelta

from app.services.recurring_transaction import (
    detect_recurring_transactions,
    normalize_description,
    detect_frequency
)
from app.models.transaction import Transaction
from app.models.recurring_transaction import RecurringTransaction

def test_normalize_description():

    text = "NETFLIX #1234 SAN FRANCISCO"

    result = normalize_description(text)

    assert "netflix" in result
    assert "1234" not in result

def test_detect_frequency_monthly():

    assert detect_frequency(30) == "monthly"
    assert detect_frequency(7) == "weekly"
    assert detect_frequency(365) == "yearly"


def test_detect_recurring_transactions_monthly(db_session):

    user_id = 1

    base_date = datetime(2024, 1, 1)

    transactions = []

    # create 4 monthly transactions
    for i in range(4):

        tx = Transaction(
            user_id=user_id,
            amount=10.0,
            type="expense",
            description="Netflix",
            created_at=base_date + timedelta(days=30 * i),
            category_id=1
        )

        db_session.add(tx)
        transactions.append(tx)

    db_session.commit()

    detect_recurring_transactions(db_session, user_id)

    results = (
        db_session.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == user_id)
        .all()
    )

    assert len(results) >= 1

    assert results[0].merchant == "netflix"

def test_not_enough_transactions(db_session):

    tx = Transaction(
        user_id=1,
        amount=50,
        type="expense",
        description="Random purchase",
        created_at=datetime.utcnow(),
        category_id=1
    )

    db_session.add(tx)
    db_session.commit()

    detect_recurring_transactions(db_session, 1)

    results = (
        db_session.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == 1)
        .all()
    )

    assert results == []

def test_fuzzy_grouping(db_session):

    user_id = 1

    tx1 = Transaction(
        user_id=user_id,
        amount=10,
        type="expense",
        description="Netflix",
        created_at=datetime.utcnow(),
        category_id=1
    )

    tx2 = Transaction(
        user_id=user_id,
        amount=10,
        type="expense",
        description="netflix subscription",
        created_at=datetime.utcnow() + timedelta(days=30),
        category_id=1
    )

    db_session.add_all([tx1, tx2])
    db_session.commit()

    detect_recurring_transactions(db_session, user_id)

    results = db_session.query(RecurringTransaction).all()

    assert len(results) == 1

def test_amount_variance_rejection(db_session):

    user_id = 1

    base_date = datetime.utcnow()

    tx1 = Transaction(
        user_id=user_id,
        amount=10,
        type="expense",
        description="Spotify",
        created_at=base_date,
        category_id=1
    )

    tx2 = Transaction(
        user_id=user_id,
        amount=200,  # huge jump
        type="expense",
        description="Spotify premium",
        created_at=base_date + timedelta(days=30),
        category_id=1
    )

    db_session.add_all([tx1, tx2])
    db_session.commit()

    detect_recurring_transactions(db_session, user_id)

    results = db_session.query(RecurringTransaction).all()

    assert results == []

def test_next_expected_date(db_session):

    user_id = 1

    base_date = datetime(2024, 1, 1)

    for i in range(3):
        db_session.add(
            Transaction(
                user_id=user_id,
                amount=10,
                type="expense",
                description="Gym",
                created_at=base_date + timedelta(days=30 * i),
                category_id=1
            )
        )

    db_session.commit()

    detect_recurring_transactions(db_session, user_id)

    result = db_session.query(RecurringTransaction).first()

    assert result.next_expected_date is not None