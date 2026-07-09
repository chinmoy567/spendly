Plan: Date Filter for Profile Page

 Context

 Step 4 (Profile Page) is implemented — it shows the logged-in user's name, email, total
 spending, expense count, and 5 most recent expenses, all pulled from
 get_expenses_by_user() with no date filtering. Spec 05_date_filter.md calls for adding an
 optional date-range filter to that same page so users can narrow the expense view (and
 the summary stats) to a specific period, without adding new routes, tables, or
 dependencies. This plan implements that spec.

 Approach

 1. database/db.py — add get_expenses_by_user_date_range(user_id, start_date, end_date)
 - Follows the exact connection/closing pattern already used in get_expenses_by_user()
 - WHERE user_id = ? always applies; date >= ? and date <= ? clauses are added
 conditionally depending on which of start_date/end_date are non-None
 - ORDER BY date DESC, same as the existing function
 - When both start_date and end_date are None, behavior is equivalent to the existing
 unfiltered query

 2. app.py — /profile route
 - Read start_date and end_date via request.args.get(...)
 - Validate format against YYYY-MM-DD (matches the stored date column format); an
 unparseable value is treated as absent rather than raising
 - If both dates are valid and start_date > end_date, set an error message and fall back
 to showing unfiltered expenses (matches the spec's DoD line for this case)
 - Otherwise call the new date-range helper if any valid date param is present, else keep
 calling the existing get_expenses_by_user()
 - Recompute total_spending, expense_count, and the recent-expenses list from the filtered
 set, replacing today's expenses[:5] computed from the full set
 - Pass start_date, end_date, and error (if any) to the template so the form/subtitle can
 reflect current filter state

 3. templates/profile.html
 - Add a filter form inside .expenses-card, above .expenses-list, method GET targeting
 url_for('profile') — GET keeps the filter state in the URL (bookmarkable, persists across
 refresh, per spec)
 - Two date inputs (type="date", names start_date/end_date), pre-filled with current
 query-string values
 - New .filter-row CSS class (flex layout) to lay the two inputs and submit button
 horizontally — reuses existing --ink, --border, --accent, --radius-sm variables, no new
 colors
 - Submit button uses the existing small .btn-primary/.btn-ghost style rather than the
 full-width .btn-submit used on auth forms
 - Error (if present) renders with the existing .auth-error class above the filter row
 - Subtitle switches between the default "Here's your spending summary" and an
 active-filter variant like "Expenses from Jan 1 to Jan 31" when filter params are set
 - Empty-state message switches between "No expenses yet" (true empty account) and "No
 expenses found in this date range" (filter yields zero results)

 4. static/css/style.css
 - Add the one new .filter-row rule; no other new styles needed — everything else reuses
 .form-group/.form-input/.auth-error/.empty-state already defined for other pages

 Files touched

 - database/db.py — add one function
 - app.py — modify /profile route body only
 - templates/profile.html — add filter form, conditional subtitle/empty-state text
 - static/css/style.css — add .filter-row

 No new routes, tables, columns, or pip packages.

 Verification

 - Run python app.py (port 5001), log in as the seeded demo user (demo@spendly.com /
 demo123)
 - /profile with no query params: confirm all 8 seeded expenses, totals, and count are
 unchanged (regression check)
 - Apply a date range covering a subset of the seeded expenses (all seeded dates fall in
 the current month): confirm list, total, and count update to match only the in-range rows
 - Submit start_date after end_date: confirm the error message appears and expenses fall
 back to the unfiltered view
 - Apply a range with no matching expenses: confirm the "no expenses found in this date
 range" message
 - Reload the resulting URL directly: confirm the date inputs stay populated and the same
 filtered results reappear
 - Clear both date fields and resubmit: confirm it returns to the full unfiltered list