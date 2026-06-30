# Spec: Registration

## Overview
Implement the registration flow so new users can create a Spendly account. The `/register` route currently only renders the existing `register.html` template (GET); this step adds POST handling that validates the form, hashes the password with Werkzeug, inserts a row into the `users` table (created in Step 01), and logs the user in by storing their `user_id` in the Flask session. This is the entry point for authentication — every later logged-in feature (profile, expenses, logout) depends on the session being set here.

## Depends on
- Step 01 — Database setup. The `users` table with `UNIQUE(email)` and `password_hash` columns must exist.

## Routes
- `GET /register` — Render the registration form. Redirect already-authenticated users to `/`. **public**
- `POST /register` — Validate form input, hash password, insert user, start session, redirect to `/`. On failure re-render the form with an error. **public**

## Database changes
No database changes. The `users` table from Step 01 is sufficient:
- `id` (PK), `name`, `email` (UNIQUE), `password_hash`, `created_at`

## Templates
- **Modify:** `templates/register.html` — the form already posts to `/register` with `name`, `email`, `password`. No structural change needed; the template already renders `{% if error %}` and the `auth-error` class.
- **Create:** none

## Files to change
- `app.py` — Convert `/register` from a one-line `render_template` into a function that branches on `request.method`. Add `GET` (redirect-if-logged-in) and `POST` (validate → insert → login → redirect) branches. Add the session secret-key config.
- `templates/register.html` — No change expected; spec assumes current markup is final. Verify error rendering works once backend is wired up.

## Files to create
None

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already used in `seed_db()` (Step 01).

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `database.db.get_db()`.
- All SQL must be parameterised (`?` placeholders). Never use f-strings or `.format()` in SQL.
- Passwords must be hashed with `werkzeug.security.generate_password_hash` (default `pbkdf2:sha256`).
- On successful registration, store `session["user_id"] = user.id`. Do NOT log in by setting a cookie manually.
- Set a `SECRET_KEY` on the Flask app (read from env `SPENDLY_SECRET_KEY`, fall back to a hardcoded dev string for now). Document the env var in a comment.
- Validation rules (server-side):
  - `name`: stripped, non-empty, max 100 chars.
  - `email`: stripped, lowercased, must match a basic email regex (`[^@\s]+@[^@\s]+\.[^@\s]+`), max 254 chars.
  - `password`: min 8 chars, max 128 chars.
  - On any failure → re-render `register.html` with a single error string (e.g. `"Email already registered"`, `"Password must be at least 8 characters"`). Keep error messages user-friendly; do not leak whether the email exists if the failure is for another reason.
  - Pre-check email uniqueness via `SELECT 1 FROM users WHERE email = ?` and return `"Email already registered"` if found — this matches the friendly-message rule because the email field is the one being submitted.
- On duplicate-email race (UNIQUE constraint violation on INSERT), treat the same as the pre-check — show `"Email already registered"`.
- Redirect target after successful registration: `/` (landing page). Logged-in users hitting `/register` should also be redirected to `/`.
- Use CSS variables from `static/css/style.css` for any new styling — never hardcode hex values.
- All templates extend `base.html`.
- Currency is irrelevant to this step — registration has no monetary fields.

## Definition of done
- [ ] `python app.py` starts without errors on port 5001.
- [ ] `GET /register` renders the existing form.
- [ ] `POST /register` with valid name + email + password (≥8 chars) inserts a new row in `users` and redirects to `/`.
- [ ] The new user's `password_hash` in `users` is a Werkzeug hash (starts with `pbkdf2:` or `scrypt:`), never plaintext.
- [ ] `POST /register` with a duplicate email re-renders the form with the error `"Email already registered"` and does NOT insert a row.
- [ ] `POST /register` with password < 8 chars re-renders the form with an error and does NOT insert a row.
- [ ] `POST /register` with an invalid email format re-renders the form with an error and does NOT insert a row.
- [ ] After successful registration, `session["user_id"]` is set (verifiable via a temporary `print(session)` or by checking Flask's session cookie is non-empty).
- [ ] Visiting `/register` while already logged in redirects to `/`.
- [ ] All SQL queries use `?` placeholders — no f-strings or `.format()` in SQL strings.
- [ ] No new pip packages added to `requirements.txt`.