# Plan: Database Setup (Step 1)

## Context

Spendly's `database/db.py` is currently just a comment stub — no working code. Per `.claude/specs/01_database_setup.md`, this is the first implementation step and establishes the data layer (users + expenses tables) that every future feature (auth, profile, expense tracking) depends on. Nothing else should be implemented yet — the stub routes in `app.py` stay untouched.

Key decision confirmed by reading `.gitignore`: it already lists the literal filename `expense_tracker.db`, which resolves the spec's "`spendly.db` (or `expense_tracker.db`)" ambiguity — the DB file must be `expense_tracker.db` in the project root.

No existing tests reference `get_db`/`init_db`/`seed_db` or impose any other filename/schema constraints (confirmed via exploration — no `tests/` directory exists yet).

## Changes

### 1. `database/db.py` — full implementation

Replace the stub with:

- Module-level path resolution so the DB always lands in the project root regardless of CWD:
  ```python
  BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")
  ```
- **`get_db()`**: opens `sqlite3.connect(DB_PATH)`, sets `row_factory = sqlite3.Row`, executes `PRAGMA foreign_keys = ON`, returns the connection. Does not close it — caller's responsibility.
- **`init_db()`**: opens its own connection via `get_db()`, runs `CREATE TABLE IF NOT EXISTS` for `users` and `expenses` (expenses has `FOREIGN KEY (user_id) REFERENCES users (id)`), commits, closes. `created_at` uses `DEFAULT (datetime('now'))` (parens required for a non-constant SQLite default).
- **`seed_db()`**: opens its own connection, checks `SELECT COUNT(*) AS count FROM users`; if any rows exist, closes and returns immediately (idempotent — never duplicates). Otherwise inserts:
  - One demo user: name `Demo User`, email `demo@spendly.com`, password hashed via `generate_password_hash("demo123")`.
  - 8 sample expenses tied to that user's `lastrowid`, spread across the current month using `datetime.now().year/.month` + fixed day-of-month values (all ≤ 28, safe for February), covering all 7 categories with Food repeating once:

    | day | category      | amount | description       |
    | --- | ------------- | ------ | ----------------- |
    | 3   | Food          | 45.50  | Grocery shopping  |
    | 5   | Transport     | 20.00  | Bus fare          |
    | 7   | Bills         | 120.00 | Electricity bill  |
    | 10  | Health        | 35.75  | Pharmacy          |
    | 14  | Entertainment | 15.00  | Movie ticket      |
    | 18  | Shopping      | 60.25  | Clothing          |
    | 22  | Other         | 25.00  | Miscellaneous     |
    | 26  | Food          | 32.40  | Restaurant dinner |

- No `try/except` anywhere in this file — per spec §13, invalid SQL/FK/UNIQUE violations must propagate as normal exceptions, not be swallowed.
- All queries parameterized (`?` placeholders) — no f-strings in SQL, per project code style.

### 2. `app.py` — wire up initialization

- Add import: `from database.db import get_db, init_db, seed_db` (right after the `flask` import). `get_db` is imported now even though unused here yet, per spec §6 — later steps will use it directly in routes.
- Immediately after `app = Flask(__name__)`, add:
  ```python
  with app.app_context():
      init_db()
      seed_db()
  ```
  Placing this at module level (before route definitions) ensures the DB exists before any route runs, whether the app starts via `python app.py` or is imported by a test client.
- No other lines change — all 5 implemented routes, all 5 stub routes (still plain-string returns), and the `if __name__ == "__main__": app.run(debug=True, port=5001)` block stay exactly as-is.

## Verification

1. Run `python app.py` from the project root — confirm no exceptions, and that `expense_tracker.db` is created in the project root (not inside `database/`).
2. Run it a second time — confirm no duplicate demo user/expenses are inserted (seed check works).
3. Inspect the DB (e.g. `sqlite3 expense_tracker.db` or a quick Python REPL check) to confirm:
   - `users` table has exactly 1 row (Demo User, hashed password, not plaintext `demo123`).
   - `expenses` table has exactly 8 rows, all `user_id` matching the demo user, dates all in the current `YYYY-MM`, all 7 categories represented.
   - `PRAGMA foreign_keys` reports `1` (on) for a connection from `get_db()`.
4. Confirm existing routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) still render correctly and stub routes still return their placeholder strings — no regression.
