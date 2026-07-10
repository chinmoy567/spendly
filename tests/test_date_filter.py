"""Tests for the date filter feature on the profile page."""

import pytest
import tempfile
import os
from app import app
from database.db import get_db, init_db, get_expenses_by_user_date_range
from werkzeug.security import generate_password_hash


@pytest.fixture
def test_app():
    """Create a Flask app configured for testing."""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()

    # Set up the app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    # Monkey-patch the DB_PATH in the db module
    import database.db as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = db_path

    with app.app_context():
        init_db()

    yield app

    # Cleanup
    db_module.DB_PATH = original_db_path
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_app):
    """Create a test client with a fresh database."""
    return test_app.test_client()


@pytest.fixture
def setup_test_data(test_app):
    """Set up test data and return user ID."""
    with test_app.app_context():
        password_hash = generate_password_hash("test_password")
        conn = get_db()

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Test User", "test@example.com", password_hash)
        )
        user_id = cursor.lastrowid

        # Add test expenses with various dates
        expenses = [
            (50.00, "Food", "2026-07-01", "Early month expense"),
            (30.00, "Transport", "2026-07-10", "Mid-early expense"),
            (45.00, "Entertainment", "2026-07-15", "Mid-month expense"),
            (25.00, "Shopping", "2026-07-20", "Mid-late expense"),
            (60.00, "Bills", "2026-07-25", "Late month expense"),
            (35.00, "Health", "2026-08-05", "Next month expense"),
        ]

        for amount, category, date_str, description in expenses:
            conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, category, date_str, description)
            )

        conn.commit()
        conn.close()

    return user_id


@pytest.fixture
def authenticated_client(client, test_app, setup_test_data):
    """Create a test client with an authenticated user."""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test_password'
    }, follow_redirects=True)
    return client


class TestDateFilterDatabase:
    """Test the get_expenses_by_user_date_range() database function."""

    def test_get_expenses_by_user_date_range_all_dates(self, test_app, setup_test_data):
        """Test retrieving expenses without date filters."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(user_id)
            assert len(expenses) == 6
            # Ordered by date DESC, so latest first
            assert expenses[0]["date"] == "2026-08-05"
            assert expenses[-1]["date"] == "2026-07-01"

    def test_get_expenses_by_user_date_range_with_start_date(self, test_app, setup_test_data):
        """Test retrieving expenses with only start date."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(user_id, start_date="2026-07-20")
            # Should get 3 expenses: 07-20, 07-25, and 08-05
            assert len(expenses) == 3
            assert all(e["date"] >= "2026-07-20" for e in expenses)

    def test_get_expenses_by_user_date_range_with_end_date(self, test_app, setup_test_data):
        """Test retrieving expenses with only end date."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(user_id, end_date="2026-07-15")
            assert len(expenses) == 3
            assert all(e["date"] <= "2026-07-15" for e in expenses)

    def test_get_expenses_by_user_date_range_with_both_dates(self, test_app, setup_test_data):
        """Test retrieving expenses with both start and end dates."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(
                user_id,
                start_date="2026-07-10",
                end_date="2026-07-25"
            )
            assert len(expenses) == 4  # 07-10, 07-15, 07-20, 07-25
            assert all("2026-07-10" <= e["date"] <= "2026-07-25" for e in expenses)

    def test_get_expenses_by_user_date_range_no_matches(self, test_app, setup_test_data):
        """Test retrieving expenses when no expenses match the date range."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(
                user_id,
                start_date="2026-09-01",
                end_date="2026-09-30"
            )
            assert len(expenses) == 0

    def test_get_expenses_by_user_date_range_exact_dates(self, test_app, setup_test_data):
        """Test filtering with inclusive date boundaries."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(
                user_id,
                start_date="2026-07-15",
                end_date="2026-07-15"
            )
            assert len(expenses) == 1
            assert expenses[0]["date"] == "2026-07-15"

    def test_get_expenses_by_user_date_range_ordering(self, test_app, setup_test_data):
        """Test that expenses are ordered by date DESC (newest first)."""
        with test_app.app_context():
            user_id = setup_test_data
            expenses = get_expenses_by_user_date_range(user_id)
            # Verify ordering
            for i in range(len(expenses) - 1):
                assert expenses[i]["date"] >= expenses[i + 1]["date"]


class TestDateFilterRoute:
    """Test the /profile route with date filtering."""

    def test_profile_requires_login(self, client):
        """Test that /profile redirects to login when not authenticated."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_displays_all_expenses_by_default(self, authenticated_client):
        """Test that profile displays all expenses when no filter is applied."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        # Check that profile page loads and shows expenses or proper empty state
        assert b"Here's your spending summary" in response.data or b"spending" in response.data.lower()

    def test_profile_filters_by_start_date(self, authenticated_client):
        """Test filtering expenses by start date."""
        response = authenticated_client.get('/profile?start_date=2026-07-20')
        assert response.status_code == 200
        # Should show expenses from 07-20 onwards (25, 08-05)
        assert b"$60.00" in response.data  # 2026-07-25 expense
        assert b"$35.00" in response.data  # 2026-08-05 expense

    def test_profile_filters_by_end_date(self, authenticated_client):
        """Test filtering expenses by end date."""
        response = authenticated_client.get('/profile?end_date=2026-07-15')
        assert response.status_code == 200
        # Should show expenses up to 07-15 (01, 10, 15)
        assert b"$50.00" in response.data  # 2026-07-01 expense
        assert b"$30.00" in response.data  # 2026-07-10 expense
        assert b"$45.00" in response.data  # 2026-07-15 expense

    def test_profile_filters_by_date_range(self, authenticated_client):
        """Test filtering expenses by both start and end dates."""
        response = authenticated_client.get('/profile?start_date=2026-07-10&end_date=2026-07-25')
        assert response.status_code == 200
        # Should include: 2026-07-10, 2026-07-15, 2026-07-20, 2026-07-25
        assert b"$30.00" in response.data  # 2026-07-10
        assert b"$45.00" in response.data  # 2026-07-15
        assert b"$25.00" in response.data  # 2026-07-20
        assert b"$60.00" in response.data  # 2026-07-25

    def test_profile_filters_shows_correct_totals(self, authenticated_client):
        """Test that total spending and expense count are correct for filtered results."""
        response = authenticated_client.get('/profile?start_date=2026-07-15&end_date=2026-07-25')
        assert response.status_code == 200
        # Should have: 45 + 25 + 60 = 130.00
        assert b"$130.00" in response.data

    def test_profile_filters_with_no_matches(self, authenticated_client):
        """Test that appropriate message shows when filter has no matches."""
        response = authenticated_client.get('/profile?start_date=2026-09-01&end_date=2026-09-30')
        assert response.status_code == 200
        assert b"No expenses found in this date range" in response.data or b"No expenses" in response.data

    def test_profile_filters_shows_filter_status_in_subtitle(self, authenticated_client):
        """Test that subtitle shows active date range."""
        response = authenticated_client.get('/profile?start_date=2026-07-15&end_date=2026-07-25')
        assert response.status_code == 200
        # Should show something like "Expenses from 2026-07-15 to 2026-07-25"
        assert b"Expenses from" in response.data and b"2026-07-15" in response.data

    def test_profile_invalid_date_format_ignored(self, authenticated_client):
        """Test that invalid date formats are ignored gracefully."""
        response = authenticated_client.get('/profile?start_date=invalid&end_date=2026-07-25')
        assert response.status_code == 200
        # Should respond successfully without crashing
        assert b"Profile" in response.data or b"profile" in response.data.lower()

    def test_profile_start_date_after_end_date_shows_error(self, authenticated_client):
        """Test error handling when start_date > end_date."""
        response = authenticated_client.get('/profile?start_date=2026-07-25&end_date=2026-07-15')
        assert response.status_code == 200
        # Should show error message
        assert b"Start date must be before end date" in response.data

    def test_profile_clears_filter_with_empty_dates(self, authenticated_client):
        """Test that filter is cleared when both date fields are empty."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        # Check that default subtitle is shown (not filtered subtitle)
        assert b"Here's your spending summary" in response.data

    def test_profile_preserves_filter_parameters_in_form(self, authenticated_client):
        """Test that date inputs are pre-filled with current filter values."""
        response = authenticated_client.get('/profile?start_date=2026-07-15&end_date=2026-07-25')
        assert response.status_code == 200
        # Form should have the dates as values
        assert b"2026-07-15" in response.data and b"2026-07-25" in response.data

    def test_profile_summary_stats_reflect_filtered_results(self, authenticated_client):
        """Test that total spending and count reflect filtered expenses."""
        response = authenticated_client.get('/profile?start_date=2026-07-01&end_date=2026-07-10')
        assert response.status_code == 200
        # Should have: 50 (07-01) + 30 (07-10) = 80.00
        assert b"$80.00" in response.data
