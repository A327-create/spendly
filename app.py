import os
import re
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import init_db, seed_db, get_db

# Session secret. In production set SPENDLY_SECRET_KEY in the environment;
# the fallback below is for local development only.
app = Flask(__name__)
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-only-not-for-production")


# ------------------------------------------------------------------ #
# Validation helpers                                                  #
# ------------------------------------------------------------------ #

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_registration(name, email, password):
    """Return an error message string, or None if the input is valid."""
    if not name:
        return "Please enter your name"
    if len(name) > 100:
        return "Name is too long"
    if not email:
        return "Please enter your email"
    if len(email) > 254:
        return "Email is too long"
    if not EMAIL_RE.match(email):
        return "Please enter a valid email address"
    if not password:
        return "Please enter a password"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if len(password) > 128:
        return "Password is too long"
    return None


# Login intentionally collapses every failure into a single generic
# message — never reveal whether the email exists or which field was
# wrong, to avoid leaking which accounts are registered.
_LOGIN_ERROR = "Invalid email or password"


def _validate_login(email, password):
    """Return an error message string, or None if the input is valid.

    The login side is stricter than registration in one way and looser in
    another: no password minimum (registration already enforced it), but
    every failure returns the same generic message to the caller.
    """
    if not email:
        return _LOGIN_ERROR
    if len(email) > 254:
        return _LOGIN_ERROR
    if not EMAIL_RE.match(email):
        return _LOGIN_ERROR
    if not password:
        return _LOGIN_ERROR
    if len(password) > 128:
        return _LOGIN_ERROR
    return None


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Already-logged-in users go straight to the landing page.
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        error = _validate_registration(name, email, password)
        if error:
            return render_template("register.html", error=error)

        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                return render_template(
                    "register.html", error="Email already registered"
                )

            password_hash = generate_password_hash(password)
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
            session["user_id"] = cur.lastrowid
        except sqlite3.IntegrityError:
            # UNIQUE(email) race — treat the same as the pre-check.
            return render_template(
                "register.html", error="Email already registered"
            )
        finally:
            conn.close()

        return redirect(url_for("landing"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Already-logged-in users go straight to the landing page.
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        error = _validate_login(email, password)
        if error:
            return render_template("login.html", error=error)

        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        finally:
            conn.close()

        if row is None or not check_password_hash(row["password_hash"], password):
            return render_template("login.html", error=_LOGIN_ERROR)

        session["user_id"] = row["id"]
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    # Tolerant of unauthenticated users — `session.clear()` is a no-op
    # when there's nothing to clear.
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
