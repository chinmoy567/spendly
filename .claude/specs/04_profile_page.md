# Spec: Profile Page

## Overview

Implement a user profile page that displays the logged-in user's account information and a summary of their expenses. The profile page will be the main dashboard users see after logging in, showing their name, email, total spending, expense count, and a preview of their most recent expenses. This establishes a foundation for the expense tracker and provides visual confirmation that the user is logged in.

## Depends on

Step 1: Database Setup — requires the `users` and `expenses` tables.
Step 2: Registration — requires users to exist in the database.
Step 3: Login and Logout — requires session management and authentication.

## Routes

- `GET /profile` — render user profile page with account info and expense summary — logged-in only

## Database changes

No new tables or columns needed. The `users` and `expenses` tables created in Steps 1 and 2 are sufficient.

## Templates

- **Create:** `templates/profile.html` — display logged-in user's name, email, total spending, expense count, and recent expense list

## Files to change

- `app.py` — implement full `/profile` route to fetch user data and expenses; render template with data
- `database/db.py` — add helper function `get_user_by_id()` to fetch user by ID; add helper function `get_expenses_by_user()` to fetch user's expenses
- `templates/base.html` — ensure navigation shows logged-in user name and profile/logout links

## Files to create

- `templates/profile.html` — new profile page template

## New dependencies

No new dependencies.

## Rules for implementation

- **No SQLAlchemy or ORMs** — use raw parameterized SQL only
- **Parameterised queries only** — never use f-strings or string concatenation in SQL
- **Use CSS variables** — never hardcode hex values; style consistent with existing pages
- **All templates extend `base.html`** — use `url_for()` for all internal links
- **Session check in route** — verify `user_id` in session; redirect to login if not authenticated
- **Never display raw database errors** to users — handle gracefully
- **Fetch user data only once per request** — store in variables, not repeated queries
- **Display expense summary** — show total spending (sum of all amounts), expense count, and last 5 expenses
- **Format currency** — display all amounts as `$X.XX` (not raw floats)
- **Format dates** — display dates in human-readable format (e.g., "Jan 15, 2024")
- **Empty state handling** — if user has no expenses, show a friendly message instead of an empty list
- **Links to expense routes** — prepare for future steps by adding placeholders for Edit/Delete links (not clickable yet)

## Definition of done

- [ ] GET /profile requires logged-in user (redirects to login if not)
- [ ] Route fetches user data by user_id from session
- [ ] Route fetches all expenses for the logged-in user
- [ ] Template displays user's name
- [ ] Template displays user's email
- [ ] Template displays total spending (sum of all expense amounts) formatted as currency
- [ ] Template displays expense count
- [ ] Template displays up to 5 most recent expenses (sorted by date, newest first)
- [ ] Each expense shows category, amount (formatted as currency), date (human-readable), and description
- [ ] If user has no expenses, show "No expenses yet" or similar friendly message
- [ ] All currency values display as $X.XX format
- [ ] All dates display in human-readable format (e.g., "Jan 15, 2024")
- [ ] Profile page extends `base.html` and uses `url_for()` for all links
- [ ] Navigation in `base.html` shows username and logout link when logged in
- [ ] No raw database errors shown to users
- [ ] Styling is consistent with landing, register, and login pages (uses CSS variables)
