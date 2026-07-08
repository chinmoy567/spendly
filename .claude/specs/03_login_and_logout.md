# Spec: Login and Logout

## Overview

Implement user authentication and session management for Spendly. Users will log in with email and password, which will be verified against the database. Flask sessions will store authentication state, allowing users to access protected pages. The logout route will clear the session and return users to the landing page. This establishes the core auth flow needed for the expense tracker.

## Depends on

Step 1: Database Setup — requires the `users` table and `get_db()` function.
Step 2: Registration — requires users to exist in the database.

## Routes

- `POST /login` — process login form submission; verify credentials and establish session — public
- `GET /logout` — clear session and redirect to landing page — logged-in

## Database changes

No new tables or columns needed. The `users` table created in Step 1 is sufficient.

## Templates

- **Modify:** `templates/login.html` — already exists with form structure; add POST handler to validate credentials
- **Create:** `templates/profile_stub.html` — simple page showing user is logged in (or profile placeholder for Step 4)

## Files to change

- `app.py` — add POST handler for `/login`; implement `/logout` route; add session helpers
- `templates/base.html` — add conditional nav items (logged-in user name, logout link)
- `templates/login.html` — keep form; update to use POST /login with error handling

## Files to create

- `database/helpers.py` (optional) — or add helpers directly to `database/db.py` for finding users and verifying passwords

## New dependencies

No new dependencies. Use `werkzeug.security.check_password_hash` (werkzeug already in requirements.txt).

## Rules for implementation

- **No SQLAlchemy or ORMs** — use raw parameterized SQL only
- **Parameterised queries only** — never use f-strings or string concatenation in SQL
- **Passwords verified with werkzeug** — use `check_password_hash` from `werkzeug.security`
- **Use Flask sessions** — `flask.session` to store user_id; set `app.secret_key` in `app.py`
- **Session security** — set `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SECURE = True` in Flask config
- **Use CSS variables** — never hardcode hex values; style consistent with `register.html`
- **All templates extend `base.html`** — use `url_for()` for all internal links
- **Validation on POST /login** — reject empty fields, show "invalid email or password" (never leak whether email exists)
- **POST-Redirect-GET pattern** — after successful login, redirect to a protected page or dashboard
- **Logout clears session** — `session.clear()` and redirect to `/`
- **Never display raw database errors** to users — convert to user-friendly messages

## Definition of done

- [ ] POST /login receives email and password from form
- [ ] POST /login validates email format and non-empty password
- [ ] POST /login queries database for user by email
- [ ] POST /login verifies password with `check_password_hash`
- [ ] Failed login shows "Invalid email or password" without leaking whether email exists
- [ ] Successful login stores `user_id` in Flask session
- [ ] Successful login redirects to a protected page (profile, dashboard, or placeholder)
- [ ] GET /logout clears Flask session with `session.clear()`
- [ ] GET /logout redirects to landing page `/`
- [ ] Logged-out user cannot access protected pages
- [ ] Base template shows username if logged in; shows login/register links if not logged in
- [ ] No raw database errors shown to users
- [ ] Session is httponly and secure (for HTTPS in production)
