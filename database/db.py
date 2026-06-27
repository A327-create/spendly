import os
import sqlite3
from calendar import monthrange
from datetime import date

from werkzeug.security import generate_password_hash

# Absolute path to the project root (parent of the `database/` package).
# Using __file__ makes the DB location CWD-independent — works whether the
# app is started from the project root, via `flask run`, or from elsewhere.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")


def get_db():
    """Open a SQLite connection with dictionary-like rows and FK enforcement.

    SQLite's `PRAGMA foreign_keys` is connection-scoped (not database-scoped),
    so it must be re-issued on every connection — otherwise foreign key
    constraints silently degrade to no-ops.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist.

    Safe to call repeatedly: `CREATE TABLE IF NOT EXISTS` is a no-op once the
    tables are in place.
    """
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


# ---- Seed data ----------------------------------------------------------
#
# 8 sample expenses covering all 7 fixed categories (Food appears twice for
# realism). Dates are clamped to the current calendar month via `monthrange`
# so the seed never tries to write e.g. "2026-02-30".

_today = date.today()
_year, _month = _today.year, _today.month
_last_day = monthrange(_year, _month)[1]


def _d(day):
    return f"{_year:04d}-{_month:02d}-{min(day, _last_day):02d}"


SAMPLE_EXPENSES = [
    (1500.00, "Bills",         _d(1),  "Electricity bill"),
    ( 220.50, "Food",          _d(3),  "Groceries"),
    (  85.00, "Transport",     _d(6),  "Metro card recharge"),
    ( 399.00, "Entertainment", _d(9),  "Movie tickets"),
    ( 450.00, "Health",        _d(12), "Pharmacy - vitamins"),
    ( 180.00, "Food",          _d(15), "Dinner with friends"),
    (1299.00, "Shopping",      _d(18), "Headphones"),
    ( 250.00, "Other",         _d(22), "Stationery"),
]


def seed_db():
    """Insert the demo user and 8 sample expenses on first run only.

    Idempotent: returns immediately if `users` already has any rows, so
    repeated startups never duplicate seed data.
    """
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        if count > 0:
            return

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cur.lastrowid

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [(user_id, amount, category, day, description)
             for (amount, category, day, description) in SAMPLE_EXPENSES],
        )
        conn.commit()
    finally:
        conn.close()