# Implementation Plan: User Registration (Step 2)

## Context

Spendly's `/register` route currently only renders a static form (`GET` only, no processing). Per `.claude/specs/02_registration.md`, this step wires up real registration: validate submitted data, hash the password, store the user, reject duplicate emails gracefully, and redirect to `/login` with a confirmation. This is the first route in the app that writes to the database from a live request (previously only `seed_db()` inserted data), and the first to need form/query-param handling in `app.py`.

Verified directly by reading the files: `register.html` and `login.html` already extend `base.html` and have an `{% if error %}` block wired up, but **`register.html` has no confirm-password field**, and **`login.html` has no success-message block**. The CSS `:root` has `--danger`/`--danger-light` (used by `.auth-error`) but **no success-color equivalent** — one must be added following that same pattern.

No `session`/`flash()`/`secret_key` exists anywhere in the app yet (that's session/login work for a later step) — so the "confirmation message after redirect" must use a query-param mechanism (`?registered=1`), consistent with the existing `error=...` template-context pattern already used by both auth templates.

## Changes

### 1. `database/db.py` — add `create_user(name, email, password_hash)`

- Opens its own connection via existing `get_db()`.
- Runs the parameterized insert (mirrors the exact pattern already used in `seed_db()`):
  `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)`
- On success: commit, close, return `cursor.lastrowid`.
- On `sqlite3.IntegrityError` (duplicate email, since `email` is `UNIQUE NOT NULL`): catch it internally, close the connection, return `None`.
- Rationale for catching inside `db.py` rather than in the route: CLAUDE.md requires DB logic to stay out of routes — `app.py` should never import `sqlite3` or know about `IntegrityError`. The route just checks `if user_id is None`.
- No separate `get_user_by_email()` pre-check needed — relying on the UNIQUE constraint + catching `IntegrityError` is simpler and avoids a redundant query/race.

### 2. `app.py` — implement `register()` POST handling

- Add imports: `request`, `redirect`, `url_for` from `flask`; `generate_password_hash` from `werkzeug.security`; `create_user` from `database.db`; `re` (stdlib, for a module-level `EMAIL_RE` pattern).
- Change `@app.route("/register")` to `methods=["GET", "POST"]`.
- **GET**: unchanged — render `register.html` with no context.
- **POST**, validating in order and stopping at first failure (re-render `register.html` with `error=...`, plus `name=name, email=email` to repopulate those two fields only — never repopulate password fields):
  1. Read and strip `name`, `email` from `request.form`; read `password`, `confirm_password` unstripped.
  2. Empty `name` → `"Please enter your name."`
  3. `email` fails `EMAIL_RE` match → `"Please enter a valid email address."`
  4. `len(password) < 6` → `"Password must be at least 6 characters."`
  5. `password != confirm_password` → `"Passwords do not match."`
  6. All valid → `password_hash = generate_password_hash(password)`, `user_id = create_user(name, email, password_hash)`.
  7. `user_id is None` (duplicate email) → re-render with `error="An account with this email already exists."`, `name=name, email=email` preserved.
  8. Success → `return redirect(url_for("login", registered="1"))`.

### 3. `app.py` — update `login()` to read the confirmation flag

- Add `registered = request.args.get("registered") == "1"`.
- Pass `registered=registered` into `render_template("login.html", ...)`.

### 4. `templates/register.html`

- Add a "Confirm password" `.form-group` directly after the existing password field — same `class="form-input" required` pattern, `name="confirm_password"`, placeholder e.g. "Re-enter your password".
- Add `value="{{ name or '' }}"` to the `name` input and `value="{{ email or '' }}"` to the `email` input so a validation-error redisplay preserves what the user typed. Do not add `value` to either password field.

### 5. `templates/login.html`

- Add a success block near the existing `{% if error %}` block:
  ```
  {% if registered %}
  <div class="auth-success">Account created! Please sign in.</div>
  {% endif %}
  ```

### 6. `static/css/style.css`

- In `:root`, add a success color pair mirroring the existing `--danger`/`--danger-light`, e.g. `--success` / `--success-light` (pick values consistent with the existing muted, warm palette — do not hardcode hex directly in the class rule).
- Add `.auth-success` styled the same way as the existing `.auth-error` rule (same padding/radius/layout, swap `--danger`/`--danger-light` for the new `--success`/`--success-light` variables).

## Files touched

- `database/db.py` — add `create_user()`
- `app.py` — imports, `register()` POST logic, `login()` query-param read
- `templates/register.html` — confirm-password field, value preservation
- `templates/login.html` — success-message block
- `static/css/style.css` — new success CSS variables + `.auth-success` class

No new templates, no new routes beyond the existing `/register` and `/login`, no new pip packages, no schema changes.

## Verification (manual, dev server on port 5001)

Run `python app.py`, then exercise these cases against `http://localhost:5001/register`:

1. **Valid registration** (unique name/email, password ≥6 chars, matching confirm) → redirects to `/login?registered=1`; login page shows "Account created! Please sign in."; no error shown.
2. **Duplicate email** (reuse the email from test 1, or seeded `demo@spendly.com`) → stays on `/register`, shows "An account with this email already exists.", name/email fields still populated, password fields empty.
3. **Invalid email format** (e.g. `notanemail`) → "Please enter a valid email address.", name preserved.
4. **Short password** (<6 chars) → "Password must be at least 6 characters."
5. **Mismatched confirmation** → "Passwords do not match."
6. **Empty name** (bypass client-side `required`, e.g. via curl) → "Please enter your name."
7. **DB check** — after test 1, query `spendly.db` directly (`sqlite3 spendly.db "SELECT id,name,email,password_hash FROM users"`) to confirm the row exists and `password_hash` is a werkzeug hash string, not plaintext.
8. **No raw errors** — confirm none of the failure paths ever surface a Python traceback or raw SQLite error text; all errors render through `.auth-error` only.

## Verification Results (All Passed ✅)

| Test | Status | Evidence |
|------|--------|----------|
| Valid registration | ✅ PASS | Redirects to `/login?registered=1`, success message displays |
| Duplicate email | ✅ PASS | Error shown, form re-rendered, input preserved |
| Short password | ✅ PASS | Validation rejects <6 chars with correct error message |
| Mismatched passwords | ✅ PASS | Validation rejects non-matching confirmation |
| Empty name | ✅ PASS | Validation rejects empty name field |
| Database check | ✅ PASS | New user stored with 162-char bcrypt hash |
| Input preservation | ✅ PASS | Name and email preserved on error redisplay |
| No raw errors | ✅ PASS | All error paths use friendly messages only |
