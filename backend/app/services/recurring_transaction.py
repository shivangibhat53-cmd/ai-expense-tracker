import re
import statistics
from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.transaction import Transaction
from app.models.recurring_transaction import RecurringTransaction


# -----------------------------
# NORMALIZATION
# -----------------------------
def normalize_description(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^a-z ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # remove noise words
    noise = {"subscription", "premium", "inc", "llc", "corp", "payment"}
    tokens = [t for t in text.split() if t not in noise]

    return " ".join(tokens)


# -----------------------------
# FREQUENCY DETECTION (FIXED)
# -----------------------------
def detect_frequency(avg_interval: float):

    if 6 <= avg_interval <= 8:
        return "weekly"

    if 12 <= avg_interval <= 16:
        return "biweekly"

    if 25 <= avg_interval <= 35:
        return "monthly"

    if 80 <= avg_interval <= 100:
        return "quarterly"

    if 350 <= avg_interval <= 380:
        return "yearly"   # ✅ FIXED

    return None


# -----------------------------
# CONFIDENCE
# -----------------------------
def calculate_confidence(occurrences, interval_std, amount_std, avg_amount):

    score = 100

    score -= min(interval_std * 5, 40)

    if avg_amount > 0:
        cv = amount_std / avg_amount
        score -= min(cv * 100, 30)

    if occurrences < 5:
        score -= 10

    return max(round(score, 2), 0)


# -----------------------------
# MAIN DETECTION FUNCTION
# -----------------------------
def detect_recurring_transactions(db: Session, user_id: int):

    logger.info("Starting recurring detection for user_id=%s", user_id)

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    grouped = defaultdict(list)

    # STEP 1: GROUPING
    for tx in transactions:
        if not tx.description:
            continue

        merchant = normalize_description(tx.description)
        if not merchant:
            continue

        grouped[merchant].append(tx)

    logger.info("GROUPS FOUND: %s", list(grouped.keys()))

    detected = 0   # ✅ FIXED SCOPE

    # STEP 2: ANALYSIS
    for merchant, items in grouped.items():

        if len(items) < 2:
            continue

        items.sort(key=lambda x: x.created_at)

        intervals = []

        for i in range(1, len(items)):
            diff = (items[i].created_at - items[i - 1].created_at).days
            intervals.append(diff)

        if not intervals:
            continue

        avg_interval = sum(intervals) / len(intervals)

        interval_std = statistics.stdev(intervals) if len(intervals) > 1 else 0

        frequency = detect_frequency(avg_interval)
        if not frequency:
            continue

        amounts = [tx.amount for tx in items]
        avg_amount = sum(amounts) / len(amounts)

        amount_std = statistics.stdev(amounts) if len(amounts) > 1 else 0

        # 🚨 HARD REJECTION RULE (IMPORTANT)
        if len(amounts) > 1:
            cv = amount_std / avg_amount if avg_amount > 0 else 0
            if cv > 0.25:   # allow small noise, reject big jumps
                continue

        confidence = calculate_confidence(
            len(items),
            interval_std,
            amount_std,
            avg_amount,
        )

        next_date = items[-1].created_at + timedelta(days=int(avg_interval))

        existing = (
            db.query(RecurringTransaction)
            .filter(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.merchant == merchant,
            )
            .first()
        )

        if existing:
            existing.frequency = frequency
            existing.average_amount = avg_amount
            existing.confidence = confidence
            existing.next_expected_date = next_date
            existing.occurrences = len(items)

        else:
            db.add(
                RecurringTransaction(
                    user_id=user_id,
                    merchant=merchant,
                    frequency=frequency,
                    average_amount=avg_amount,
                    confidence=confidence,
                    occurrences=len(items),
                    next_expected_date=next_date,
                )
            )
            detected += 1

    db.commit()

    logger.info(
        "Recurring detection completed. %s merchants detected.",
        detected,
    )

    return detected