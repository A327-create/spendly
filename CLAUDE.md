# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Spendly** — a personal expense tracker (Flask + SQLite + Jinja templates). Currency throughout the UI is rendered as `₹` (rupees).

This is an in-progress student/learning build. Several core files are intentionally scaffolded as placeholders that future steps will fill in:

- `database/db.py` — empty; expects `get_db()`, `init_db()`, `seed_db()` per its header comment.
- `static/js/main.js` — empty placeholder; JS for new features goes here or in `{% block scripts %}` of `landing.html`.
- `database/__init__.py` — empty.

The route placeholders in `app.py` (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) return plain text "coming in Step N" strings — they're not implemented yet.

## Commands

Activate the virtualenv first (Windows):

```bash
myvenv\Scripts\Activate.ps1     # PowerShell
myvenv\Scripts\activate          # cmd
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dev server (port **5001**, debug on):

```bash
python app.py
```

There are currently **no tests, no linter, and no build step** configured. The dependency list (`requirements.txt`) is Flask 3.1.3, Jinja2, Werkzeug, itsdangerous, click, blinker, colorama — nothing else.

## Architecture

Flat Flask single-app layout — no blueprints, no `models.py`, no migrations:

- `app.py` — single Flask app with all routes defined inline. Two groups of routes:
  - Implemented: `/`, `/register`, `/login`, `/terms`, `/privacy` (each just `render_template`).
  - Placeholder: `/logout`, `/profile`, `/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`.
- `database/db.py` — to be implemented. Will own the SQLite connection. The repo's `.gitignore` excludes `expense_tracker.db`.
- `templates/base.html` — shared layout: navbar, `{% block content %}`, footer with legal links, loads `css/style.css` and `js/main.js`. Templates extend it and override `title`, `content`, and optionally `head` / `scripts`.
- `templates/landing.html` — the marketing landing page. Contains a self-contained YouTube-modal block (CSS + vanilla JS at the bottom of the file) that opens when the user clicks "See how it works" (`a[href="#how-it-works"]`). The modal stops playback by clearing the iframe `src` on close. Template-specific inline styles/scripts belong at the bottom of the page that needs them — not in `base.html`.
- `templates/{register,login,terms,privacy}.html` — extend `base.html`. Terms and privacy share a `.terms-section / .terms-card` styling pattern defined in `static/css/style.css`.
- `static/css/style.css` — single site stylesheet. Defines CSS custom properties (`--ink`, `--paper`, `--paper-card`, `--border`, `--font-display`, `--font-body`, etc.) used site-wide. New page-level styles go here, keyed by the page's section class.
- `static/js/main.js` — placeholder; shared JS goes here, but page-specific JS (like the landing modal) currently lives inline at the bottom of `landing.html`.

## Conventions

- **No JS framework** — the project deliberately uses vanilla JS. Don't add a bundler, npm, or framework dependency.
- **Inline page-specific CSS/JS** lives at the bottom of the relevant template (see the `<style>` and `<script>` blocks at the end of `templates/landing.html`). Shared styles go in `static/css/style.css`.
- **Routes are flat** in `app.py` — add new routes there, don't introduce blueprints yet.
- **Currency** is always `₹` in the UI.
- **Design tokens** (colors, radii, fonts) are CSS custom properties at the top of `static/css/style.css` — reuse them rather than hardcoding values.
- **LF/CRLF warnings** on commit are expected on Windows (see `.gitignore` excludes `venv/` and `myvenv/`); the in-repo source files are stored as LF.
- **Database file** `expense_tracker.db` is git-ignored; SQLite is the assumed engine.

## Commit message style

Recent commits follow a `topic: summary` pattern (e.g. `landing: add youtube modal on see how it works click`, `landing: redesign hero section to match mockup`). Keep the same shape.