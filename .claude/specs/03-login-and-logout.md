# Spec: Login and Logout

## Overview
Wire up the existing login form so users can authenticate with email + password, and implement logout so they can end their session. The `/login` route currently only renders the template (GET); this step adds POST handling that looks up the user by email, verifies the password against the stored Werkzeug hash, and starts a session. The `/logout` placeholder currently returns a "
coming in Step 3" string; this step replaces it with a real session-clearing route. Together with Step 02 (Registration), this completes the authentication loop so the rest of the app can rely on `session["user_id"]` to identify the current user.

## Depends on
- Step 01 — Database setup. The `users` table with `password_hash` column must exist.
- Step 02 — Registration. Session helper (`session["user_id"]`) and the `app.secret_key` config are already in place.

## Routes
- `GET /login` — Render the sign-in form. Redirect already-authenticated users to `/`. **public**
- `POST /login` — Validate email + password, verify hash, start session, redirect to `/`. On failure re-render the form with a generic error. **public**
- `GET /logout` — Clear the session and redirect to `/`. **logged-in**

## Database changes
No database changes. The `users` table from Step 01 is sufficient:
- `id` (PK), `name`, `email` (UNIQUE), `password_hash`, `created_at`

## Templates
- **Modify:** `templates/login.html` — no structural change expected. The form already posts to `/login` with `email` and `password`, and already renders `{% if error %}` with the `auth-error` class. Verify error rendering works once backend is wired up.
- **Create:** none

## Files to change
- `app.py` — Convert `/login` from a one-line `render_template` into a function that branches on `request.method`. Add `GET` (redirect-if-logged-in) and `POST` (lookup → verify hash → login → redirect) branches. Add `check_password_hash` to the Werkzeug import. Add a small `_validate_login` helper (mirroring `_validate_registration`). Replace the `/logout` placeholder route with a real implementation that calls `session.clear()` and redirects to `/`.
- `templates/login.html` — No change expected; spec assumes current markup is final. Verify error rendering works once backend is wired up.

## Files to create
None

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is in the same module as `generate_password_hash` (already used in Step 02 and `seed_db`).

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` via `database.db.get_db()`.
- All SQL must be parameterised (`?` placeholders). Never use f-strings or `.format()` in SQL.
- Passwords must be verified with `werkzeug.security.check_password_hash(stored_hash, submitted_password)`. Never compare hashes as strings, and never use `==` on plaintext.
- On successful login, store `session["user_id"] = user["id"]`. Do NOT log in by setting a cookie manually.
- The `app.secret_key` is already configured in Step 02 — do not change it here.
- Validation rules (server-side):
  - `email`: stripped, lowercased, must match the existing `EMAIL_RE`, max 254 chars.
  - `password`: non-empty, max 128 chars (the login side does NOT enforce a minimum — that's a registration-only rule).
  - On any failure → re-render `login.html` with a single generic error string.
- **Generic error message:** use `"Invalid email or password"` for ALL login failures (missing email, missing password, no such user, wrong password). Do NOT reveal whether the email exists or whether the password was the wrong field — that is a user-enumeration leak. This rule overrides the registration spec's per-field error style; the login form is a single combined credential check.
- Lookup: `SELECT id, password_hash FROM users WHERE email = ?`. If no row → render the generic error. If row found → `check_password_hash(row["password_hash"], password)`; on False → render the generic error. Only on True do we set the session.
- Rate limiting, account lockout, "remember me", and password reset are explicitly **out of scope** for this step.
- Redirect target after successful login: `/` (landing page). Logged-in users hitting `/login` should also be redirected to `/`.
- `/logout` must be tolerant of being hit by an unauthenticated user — it should still clear the session and redirect to `/` without erroring. Use `session.clear()` rather than `session.pop(..., None)` to be explicit.
- Use CSS variables from `static/css/style.css` for any new styling — never hardcode hex values.
- All templates extend `base.html`.
- Currency is irrelevant to this step.

## Definition of done
- [ ] `python app.py` starts without errors on port 5001.
- [ ] `GET /login` renders the existing form.
- [ ] `POST /login` with the seeded `demo@spendly.com` / `demo123` credentials sets `session["user_id"]` and redirects to `/`.
- [ ] `POST /login` with a wrong password re-renders the form with the error `"Invalid email or password"` and does NOT set the session.
- [ ] `POST /login` with an unknown email re-renders the form with the SAME error `"Invalid email or password"` (not "user not found" or similar).
- [ ] `POST /login` with an empty email or empty password re-renders the form with the generic error and does NOT set the session.
- [ ] `POST /login` with an invalid email format re-renders the form with the generic error and does NOT set the session.
- [ ] `GET /logout` clears the session (verifiable by confirming `session["user_id"]` is gone afterwards) and redirects to `/`.
- [ ] `GET /logout` while NOT logged in still redirects to `/` without raising an error.
- [ ] Visiting `/login` while already logged in redirects to `/`.
- [ ] All SQL queries use `?` placeholders — no f-strings or `.format()` in SQL strings.
- [ ] No password comparison is done with `==` on hashes or on plaintext.
- [ ] No new pip packages added to `requirements.txt`.
