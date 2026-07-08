# Spec: Registration

## Overview

Implement the user registration flow for Spendly. Users will submit a form with their name, email, and password, which will be validated, hashed, and stored in the database. This establishes the foundation for user authentication and personalizing the expense tracking experience.

## Depends on

Step 1: Database Setup — requires the `users` table and `get_db()`, `init_db()`, `seed_db()` functions to be fully implemented.

## Routes

- `POST /register` — process registration form submission — public

## Database changes

No new tables or columns needed. The `users` table created in Step 1 is sufficient.

## Templates

- **Modify:** `templates/register.html` — convert stub to a working registration form with fields for name, email, password, and password confirmation. Display validation errors inline if submission fails.

## Files to change

- `app.py` — add POST handler for `/register`
- `templates/register.html` — build the registration form

## Files to create

None.

## New dependencies

No new dependencies. Use `werkzeug.security.generate_password_hash` (already imported in `database/db.py`).

## Rules for implementation

- **No SQLAlchemy or ORMs** — use raw parameterized SQL only
- **Parameterised queries only** — never use f-strings or string concatenation in SQL
- **Passwords hashed with werkzeug** — use `generate_password_hash` from `werkzeug.security`
- **Use CSS variables** — never hardcode hex values; style consistent with `landing.html`
- **All templates extend `base.html`** — use `url_for()` for all internal links
- **Validation happens server-side** — check email format, password strength, name not empty
- **Duplicate email rejection** — catch the `UNIQUE` constraint error and show user-friendly message
- **POST-Redirect-GET pattern** — after successful registration, redirect to `/login` with a success message
- **Never display raw database errors** to users — convert to user-friendly messages

## Definition of done

- [ ] Form displays on `GET /register`
- [ ] Form validation rejects empty fields
- [ ] Form validation rejects invalid email format (must contain `@` and domain)
- [ ] Form validation rejects short passwords (minimum 6 characters)
- [ ] Form validation rejects mismatched password confirmation
- [ ] Successful registration hashes password and stores user in database
- [ ] Duplicate email shows error message and re-renders form with user input preserved
- [ ] Successful registration redirects to `/login` with a confirmation message
- [ ] No raw database errors shown to users
- [ ] Passwords are hashed and not stored as plaintext
