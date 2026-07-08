# Implementation Plan: Login and Logout (Step 3)

## Context

Spendly currently has a working registration flow (Step 2) but `/login` only renders a static form (`GET` only) and `/logout` is a stub returning plain text. This step wires up real authentication: verify submitted credentials against the `users` table, establish a Flask session on success, protect the `/profile` stub behind that session, and clear the session on logout. This is the first time the app uses `flask.session`, so `app.secret_key` and session cookie config need to be introduced for the first time.

A key tension from CLAUDE.md: `/profile` is marked as a Step 4 stub, and "do not implement a stub route unless the active task explicitly targets that step." But this step's own Definition of Done requires "logged-out user cannot access protected pages," which needs *some* protected page to redirect to. Resolution: add a one-line session guard to the existing `/profile` stub (leaving its `"Profile page — coming in Step 4"` return string completely untouched) rather than building any new profile template or content. The guard is part of login/logout's responsibility, not profile's feature content.

**Deliberate deviation from the spec's literal text:** `.claude/specs/03_login_and_logout.md` suggests creating `templates/profile_stub.html` as an optional file. This plan skips it — building a new template is closer to "implementing the profile page" than a guard clause is, and CLAUDE.md's stub rule takes precedence. The existing plain-text stub return is reused as-is.

**Re-verified against current codebase** (fresh Explore pass): `/login` is still GET-only, `/logout` is still the plain-text stub, `get_user_by_email` still does not exist in `db.py`, no `session`/`secret_key` usage exists anywhere, `login.html`'s form already posts to `/login` with `error`/`registered` blocks ready, `base.html`'s nav is still unconditional, and neither `profile.html` nor `profile_stub.html` exists. No drift since the plan was drafted — all assumptions below still hold.

## Changes

### 1. `database/db.py` — add `get_user_by_email(email)`

```python
def get_user_by_email(email):
    """Fetch a single user row by email, or None if no match."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
```
- Reuses existing `get_db()`, parameterized query, returns `sqlite3.Row` or `None`.
- Place directly below `create_user`.

### 2. `app.py` — setup, imports

- Add `import os` (stdlib, no new dependency).
- Update flask import: `from flask import Flask, render_template, request, redirect, url_for, session`
- Update werkzeug import: `from werkzeug.security import generate_password_hash, check_password_hash`
- Update db import: `from database.db import get_db, init_db, seed_db, create_user, get_user_by_email`
- After `app = Flask(__name__)`:
  ```python
  app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
  app.config["SESSION_COOKIE_HTTPONLY"] = True
  app.config["SESSION_COOKIE_SECURE"] = True
  ```

### 3. `app.py` — `login()` becomes `GET, POST`

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = None
        if not EMAIL_RE.match(email):
            error = "Invalid email or password."
        elif not password:
            error = "Invalid email or password."

        if not error:
            user = get_user_by_email(email)
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid email or password."

        if error:
            return render_template("login.html", error=error, email=email)

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    registered = request.args.get("registered") == "1"
    return render_template("login.html", registered=registered)
```

Validation order: cheap format/empty checks first, then a single DB lookup, then password verification. **One generic error message** ("Invalid email or password.") covers every failure path — bad format, empty password, unknown email, wrong password — so there's no email-enumeration signal. `session["user_name"]` is stored alongside `user_id` at login (reusing the row already fetched — no extra query) so the nav can display a real name without new DB logic.

### 4. `app.py` — `logout()` replaces the stub

```python
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))
```

### 5. `app.py` — `profile()` gets a minimal guard only

```python
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return "Profile page — coming in Step 4"
```

Only the guard clause is added; the stub's return string stays verbatim — this is not "implementing" the profile page.

### 6. `templates/login.html`

- Fix form action: `action="/login"` → `action="{{ url_for('login') }}"` (matches register.html's pattern; never hardcode URLs per CLAUDE.md).
- Preserve email on error: add `value="{{ email or '' }}"` to the email `<input>`, mirroring register.html. Never repopulate the password field.

### 7. `templates/base.html` — conditional nav

Replace the hardcoded nav-links block:
```html
<div class="nav-links">
    {% if session.user_id %}
        <a href="{{ url_for('profile') }}">{{ session.get('user_name', 'My Profile') }}</a>
        <a href="{{ url_for('logout') }}" class="nav-cta">Sign out</a>
    {% else %}
        <a href="{{ url_for('login') }}">Sign in</a>
        <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
    {% endif %}
</div>
```
`session` is auto-injected into Jinja templates by Flask — no context processor needed.

### 8. `requirements.txt`

No changes — `check_password_hash` and `session` are already available in the pinned Flask 3.1.3 / Werkzeug 3.1.6.

## Files touched

- `database/db.py` — add `get_user_by_email()`
- `app.py` — imports, secret_key/session config, `login()` POST logic, `logout()`, `profile()` guard
- `templates/login.html` — form action fix, email value preservation
- `templates/base.html` — conditional nav (logged-in vs logged-out)

No new templates, no schema changes, no new pip packages.

## Verification (manual, dev server on port 5001)

Run `python app.py`, then exercise:

1. **Correct login** — demo user (`demo@spendly.com` / `demo123` from `seed_db()`) → redirects to `/profile`, shows stub text, nav shows "Demo User" / "Sign out".
2. **Wrong password** — correct email, bad password → re-renders `/login` with "Invalid email or password.", email pre-filled, password field empty.
3. **Unknown email** — nonexistent email → *identical* error/rendering as case 2 (no enumeration leak).
4. **Empty password** — same generic error, no traceback.
5. **Session persistence** — after login, navigate `/` then back to `/profile` — stays authenticated.
6. **Protected route enforcement** — fresh/incognito browser, visit `/profile` directly → redirects to `/login`.
7. **Logout** — while logged in, visit `/logout` → redirects to `/`, nav reverts to "Sign in"/"Get started"; re-visiting `/profile` bounces to `/login` again (confirms session actually cleared).
8. **Cookie flags** — devtools → Application → Cookies: session cookie has `HttpOnly` set. `Secure` flag means cookie only sent over HTTPS; modern browsers treat `localhost` as a secure context so this should still work in dev.
9. **Registration flow untouched** — `?registered=1` success banner still renders correctly after the new `error`/`email` template vars are added (mutually exclusive in practice).
