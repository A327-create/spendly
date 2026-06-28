"""Seed a single dummy Indian user into the database.

Reuses the get_db() helper from db.py so the connection logic (FK enforcement,
row factory, DB path) stays in one place.
"""
import os
import random
import sys

# Make `database` importable when this script is run from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash

from database.db import get_db, init_db


# Realistic Indian first + last names spanning common regions.
FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali",
    "Arjun", "Pooja", "Rohan", "Kavya", "Karthik", "Meera",
    "Aditya", "Neha", "Ravi", "Divya", "Sandeep", "Ananya",
    "Suresh", "Lakshmi", "Manoj", "Ritu", "Pradeep", "Swati",
    "Nikhil", "Deepa", "Sanjay", "Pallavi", "Vivek", "Aishwarya",
    "Arun", "Geeta", "Rajesh", "Shalini", "Mohan", "Rekha",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair",
    "Khan", "Singh", "Kumar", "Gupta", "Joshi", "Mehta",
    "Rao", "Mukherjee", "Chatterjee", "Banerjee", "Kapoor",
    "Bhat", "Pillai", "Menon", "Das", "Saxena", "Trivedi",
    "Choudhary", "Yadav", "Pandey", "Mishra", "Tiwari", "Bose",
]


def generate_unique_user(conn):
    """Pick a random name, build an email, and retry if the email collides."""
    while True:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        # 2-3 digit numeric suffix for realism.
        suffix = random.randint(10, 999)
        email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"

        existing = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing is None:
            return f"{first} {last}", email


def main():
    # Make sure the schema exists before we try to insert.
    init_db()

    conn = get_db()
    try:
        name, email = generate_unique_user(conn)
        password_hash = generate_password_hash("password123")

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        user_id = cur.lastrowid
    finally:
        conn.close()

    print("Dummy user created:")
    print(f"  id:    {user_id}")
    print(f"  name:  {name}")
    print(f"  email: {email}")


if __name__ == "__main__":
    main()
