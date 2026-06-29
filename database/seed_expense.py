"""Seed realistic dummy expenses for a specific user.

Usage: python database/seed_expense.py <user_id> <count> <months>
"""
import os
import random
import sys
from calendar import monthrange
from datetime import date, timedelta

# Make `database` importable when run from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db, DB_PATH


# (label, min, max, sample descriptions)
CATEGORIES = [
    ("Food",          50,  800,  [
        "Groceries", "Lunch", "Dinner with friends", "Chai and snacks",
        "Breakfast", "Street food", "Weekly veggies", "Fruits",
    ]),
    ("Transport",     20,  500,  [
        "Metro card recharge", "Auto rickshaw", "Uber ride", "Petrol",
        "Bus pass", "Rapido", "Train ticket",
    ]),
    ("Bills",         200, 3000, [
        "Electricity bill", "Internet bill", "Mobile recharge",
        "Gas cylinder", "Water bill", "DTH recharge",
    ]),
    ("Health",        100, 2000, [
        "Pharmacy - vitamins", "Doctor consultation", "Lab tests",
        "Gym membership", "Health supplements",
    ]),
    ("Entertainment", 100, 1500, [
        "Movie tickets", "OTT subscription", "Concert ticket",
        "Coffee at cafe", "Book purchase",
    ]),
    ("Shopping",      200, 5000, [
        "Headphones", "T-shirt", "Shoes", "Kitchen utensil",
        "Phone cover", "Backpack",
    ]),
    ("Other",         50,  1000, [
        "Stationery", "Haircut", "Gift", "Household supplies",
        "Donation", "Laundry",
    ]),
]

# Weighted distribution: Food most common, Health/Entertainment least.
WEIGHTED_CATEGORIES = (
    [("Food", 0)] * 28 +
    [("Transport", 1)] * 20 +
    [("Shopping", 5)] * 16 +
    [("Bills", 2)] * 14 +
    [("Other", 6)] * 10 +
    [("Entertainment", 4)] * 7 +
    [("Health", 3)] * 5
)


def _category_by_index(idx):
    return CATEGORIES[idx]


def _random_date_in_past_months(months):
    """Return a random date within the past `months` calendar months, ending today."""
    today = date.today()
    # Earliest day is the 1st of (current_month - months + 1). months=1 means this month only.
    if months <= 1:
        start = today.replace(day=1)
    else:
        # Walk back `months - 1` full months, then to day 1.
        year = today.year
        month = today.month - (months - 1)
        while month <= 0:
            month += 12
            year -= 1
        start = date(year, month, 1)

    span_days = (today - start).days
    return start + timedelta(days=random.randint(0, span_days))


def generate_expense():
    cat_idx = random.choice(WEIGHTED_CATEGORIES)[1]
    name, lo, hi, descs = _category_by_index(cat_idx)
    amount = round(random.uniform(lo, hi), 2)
    description = random.choice(descs)
    return name, amount, description


def main():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        # Pre-generate all rows so we can show date range + sample after the insert.
        rows = []
        for _ in range(count):
            category, amount, description = generate_expense()
            d = _random_date_in_past_months(months)
            rows.append((user_id, amount, category, d.isoformat(), description))

        # Single transaction — rollback on any failure.
        try:
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        dates = sorted(r[3] for r in rows)
        sample = random.sample(rows, min(5, len(rows)))

        print(f"Inserted {len(rows)} expenses for user id {user_id}.")
        print(f"Date range: {dates[0]}  to  {dates[-1]}")
        print("Sample records (user_id, amount, category, date, description):")
        for r in sample:
            print(f"  {r}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
