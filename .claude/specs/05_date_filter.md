# Spec: Date Filter for Profile Page

## Overview

Add date filtering functionality to the profile page to allow users to view expenses within a specific date range. This feature enables users to analyze their spending patterns across different time periods, making it easier to understand their expenses for specific months, quarters, or custom date ranges. The profile page will display a date range picker and filter the expense list accordingly, while maintaining all existing functionality for users who don't use the filter.

## Depends on

Step 1: Database Setup — requires the `users` and `expenses` tables.
Step 2: Registration — requires users to exist in the database.
Step 3: Login and Logout — requires session management and authentication.
Step 4: Profile Page — requires the existing profile page implementation with expenses display.

## Routes

No new routes. The existing `GET /profile` route will be enhanced to accept optional query parameters for date filtering.

## Database changes

No database changes. Date filtering is performed using existing `date` column in the `expenses` table via SQL `WHERE` clauses.

## Templates

- **Modify:** `templates/profile.html` — add date range filter UI (start date and end date inputs) above the expenses list; update expense display to reflect filtered results

## Files to change

- `app.py` — enhance `/profile` route to accept optional `start_date` and `end_date` query parameters; filter expenses by date range; pass filter state to template
- `database/db.py` — add helper function `get_expenses_by_user_date_range()` to fetch expenses within a date range
- `templates/profile.html` — add date range filter form with date inputs and submit button; display active filter status; update summary stats to reflect filtered expenses

## Files to create

No new files.

## New dependencies

No new dependencies.

## Rules for implementation

- **No SQLAlchemy or ORMs** — use raw parameterized SQL only
- **Parameterised queries only** — never use f-strings or string concatenation in SQL
- **Use CSS variables** — never hardcode hex values; style consistent with existing pages
- **All templates extend `base.html`** — use `url_for()` for all internal links
- **Date validation** — ensure start_date is not after end_date; handle invalid date formats gracefully
- **Optional filtering** — if no dates provided, display all expenses (current behavior)
- **Query parameter handling** — use `request.args.get()` for date filter parameters
- **Summary stats filtering** — total spending and expense count should reflect filtered results, not all expenses
- **URL preservation** — date filter parameters should persist when refreshing the page
- **User-friendly defaults** — date inputs should use HTML5 date type for calendar picker UX
- **Timezone awareness** — treat all dates as local dates (no timezone conversion)

## Definition of done

- [ ] Profile page displays date range filter UI with start and end date inputs
- [ ] Date inputs use HTML5 date type with browser calendar picker
- [ ] Filter form has a submit button to apply the filter
- [ ] Route accepts optional `start_date` and `end_date` query parameters
- [ ] Route validates date parameters and handles invalid formats gracefully
- [ ] Expenses are filtered to show only those within the date range (inclusive)
- [ ] If start_date is provided without end_date, show expenses from start_date onwards (to today)
- [ ] If end_date is provided without start_date, show expenses up to end_date (from beginning)
- [ ] If both dates provided and start_date > end_date, show error message (e.g., "Start date must be before end date")
- [ ] Summary stats (total spending and expense count) reflect filtered results, not all expenses
- [ ] Filtered expenses still display category, amount (formatted as currency), date (human-readable), and description
- [ ] Empty state message displays if no expenses match the filter ("No expenses found in this date range")
- [ ] Page title or subtitle indicates which filter is active (e.g., "Expenses from Jan 1 to Jan 31")
- [ ] Date filter parameters are included in page URLs (e.g., `/profile?start_date=2024-01-01&end_date=2024-01-31`)
- [ ] Removing dates from filter (clearing inputs) returns to showing all expenses
- [ ] All dates display in human-readable format (e.g., "Jan 15, 2024")
- [ ] No raw database errors shown to users
- [ ] Styling is consistent with existing profile page (uses CSS variables)
