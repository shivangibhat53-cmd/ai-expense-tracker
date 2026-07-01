import re
import statistics
from collections import defaultdict
from datetime import timedelta

from rapidfuzz import fuzz

from app.models.transaction import Transaction

def normalize_description(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # remove numbers (card ids, txn ids)
    text = re.sub(r"\d+", "", text)

    # remove special characters
    text = re.sub(r"[^a-z ]", " ", text)

    # collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

def find_or_create_group(merchant, groups, threshold=85):
    """
    groups = {
        "netflix": [...],
        "amazon": [...]
    }
    """

    for existing in groups.keys():
        score = fuzz.ratio(merchant, existing)

        if score >= threshold:
            return existing

    return merchant

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
        return "yearly"

    return None
def calculate_confidence(occurrences, interval_std, amount_std, avg_amount):

    score = 100

    # time stability
    score -= min(interval_std * 5, 40)

    # amount stability
    if avg_amount > 0:
        cv = amount_std / avg_amount
        score -= min(cv * 100, 30)

    # sample size penalty
    if occurrences < 5:
        score -= 10

    return max(round(score, 2), 0)

def detect_recurring_transactions(db, user_id: int):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    # STEP 1: GROUP BY MERCHANT (FUZZY)
    grouped = defaultdict(list)

    for tx in transactions:

        if not tx.description:
            continue

        merchant = normalize_description(tx.description)

        if not merchant:
            continue

        group_key = find_or_create_group(
            merchant,
            grouped
        )

        grouped[group_key].append(tx)

    results = []

    # STEP 2: ANALYZE EACH GROUP
    for merchant, items in grouped.items():

        if len(items) < 3:
            continue  # minimum threshold

        # sort by time
        items.sort(key=lambda x: x.created_at)

        # STEP 3: INTERVALS
        intervals = []

        for i in range(1, len(items)):
            diff = (
                items[i].created_at
                - items[i - 1].created_at
            ).days
            intervals.append(diff)

        if not intervals:
            continue

        avg_interval = sum(intervals) / len(intervals)

        interval_std = (
            statistics.stdev(intervals)
            if len(intervals) > 1
            else 0
        )

        # reject unstable patterns
        if interval_std > 8:
            continue

        frequency = detect_frequency(avg_interval)

        if not frequency:
            continue

        # STEP 4: AMOUNT ANALYSIS
        amounts = [tx.amount for tx in items]

        avg_amount = sum(amounts) / len(amounts)

        amount_std = (
            statistics.stdev(amounts)
            if len(amounts) > 1
            else 0
        )

        if avg_amount > 0:
            cv = amount_std / avg_amount
            if cv > 0.20:
                continue

        # STEP 5: CONFIDENCE
        confidence = calculate_confidence(
            len(items),
            interval_std,
            amount_std,
            avg_amount
        )

        # STEP 6: NEXT EXPECTED DATE
        next_date = items[-1].created_at + timedelta(
            days=int(avg_interval)
        )

        results.append({
            "merchant": merchant,
            "frequency": frequency,
            "occurrences": len(items),
            "average_amount": round(avg_amount, 2),
            "confidence": confidence,
            "next_expected_date": next_date
        })

    # highest confidence first
    return sorted(
        results,
        key=lambda x: x["confidence"],
        reverse=True
    )