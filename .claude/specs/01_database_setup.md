# Database Setup Specification

## 1. Overview

Replace the stub in `database/db.py` with a fully functional SQLite implementation.

This establishes the **data layer foundation** for the Spendly application.

All future features—including authentication, user profiles, and expense tracking—depend on this implementation.

---

## 2. Dependencies

**Depends On:** None

This is the first implementation step of the project.

---

## 3. Routes

No new API routes are required.

Existing placeholder routes in `app.py` should remain unchanged.

---

## 4. Database Schema

### Users Table

| Column | Type | Constraints |
|---------|------|-------------|
| id | INTEGER | Primary Key, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT `datetime('now')` |

---

### Expenses Table

| Column | Type | Constraints |
|---------|------|-------------|
| id | INTEGER | Primary Key, AUTOINCREMENT |
| user_id | INTEGER | Foreign Key → users.id, NOT NULL |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (`YYYY-MM-DD`) |
| description | TEXT | NULLABLE |
| created_at | TEXT | DEFAULT `datetime('now')` |

---

## 5. Functions to Implement

### `get_db()`

Responsibilities:

- Open a connection to `spendly.db` (or `expense_tracker.db`) in the project root.
- Configure:

  - `row_factory = sqlite3.Row`
  - `PRAGMA foreign_keys = ON`

- Return the database connection.

---

### `init_db()`

Responsibilities:

- Create the `users` table if it does not already exist.
- Create the `expenses` table if it does not already exist.
- Use `CREATE TABLE IF NOT EXISTS`.
- Be safe to call multiple times.

---

### `seed_db()`

Responsibilities:

- Check whether the `users` table already contains data.
- If data exists, exit immediately without inserting anything.
- Otherwise:

Create one demo user:

- Name: `Demo User`
- Email: `demo@spendly.com`
- Password: `demo123` (hashed using `werkzeug.security.generate_password_hash`)

Create **8 sample expenses**:

- Linked to the demo user.
- Spread across the current month.
- Cover multiple categories.
- Include at least one expense from every category.

---

## 6. Changes to `app.py`

Import:

- `get_db`
- `init_db`
- `seed_db`

Inside `app.app_context()`:

- Call `init_db()`
- Call `seed_db()`

Ensure the database is initialized before any routes are used.

---

## 7. Files to Modify

- `database/db.py`
- `app.py`

---

## 8. Files to Create

None.

---

## 9. Dependencies

Do not install any new packages.

Use only:

- `sqlite3` (Python standard library)
- `werkzeug.security`

---

## 10. Expense Categories

Use **only** these category values:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

---

## 11. Implementation Rules

- Do **not** use an ORM (e.g., SQLAlchemy).
- Use **parameterized SQL queries only**.
- Never build SQL using string formatting.
- Enable `PRAGMA foreign_keys = ON` for every database connection.
- Store `amount` as `REAL`.
- Hash passwords using:

```python
from werkzeug.security import generate_password_hash
```

- `seed_db()` must never insert duplicate data.
- Store all dates in `YYYY-MM-DD` format.

---

## 12. Expected Behavior

### `get_db()`

- Returns a valid SQLite connection.
- Supports dictionary-style row access.
- Enables foreign key enforcement.

### `init_db()`

- Creates required tables safely.
- Can be executed repeatedly without errors.

### `seed_db()`

- Inserts demo data only once.
- Prevents duplicate records on repeated executions.

The database must enforce:

- Unique email addresses.
- Valid foreign key relationships.

---

## 13. Error Handling

The implementation should behave as follows:

- Duplicate email → SQLite `UNIQUE` constraint error.
- Invalid `user_id` → SQLite foreign key constraint error.
- Invalid SQL → Raise clear exceptions for debugging.

---

## 14. Acceptance Criteria

- Database file is created automatically.
- Users table exists.
- Expenses table exists.
- Demo user is inserted.
- Password is securely hashed.
- Eight sample expenses are inserted.
- Seed data is never duplicated.
- Application starts without errors.
- Foreign key constraints are enforced.
- All SQL queries are parameterized.