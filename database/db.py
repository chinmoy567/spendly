"""SQLite helpers for Spendly: connection setup, schema creation, and seed data."""

import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")


def get_db():
    """Open a connection to the SQLite database with row access and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they do not already exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def create_user(name, email, password_hash):
    """Insert a new user into the database. Returns user_id on success, None if email already exists."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def seed_db():
    """Insert one demo user and 8 sample expenses, but only if users table is empty."""
    conn = get_db()

    row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if row["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    now = datetime.now()
    year, month = now.year, now.month

    sample_expenses = [
        (3, "Food", 45.50, "Grocery shopping"),
        (5, "Transport", 20.00, "Bus fare"),
        (7, "Bills", 120.00, "Electricity bill"),
        (10, "Health", 35.75, "Pharmacy"),
        (14, "Entertainment", 15.00, "Movie ticket"),
        (18, "Shopping", 60.25, "Clothing"),
        (22, "Other", 25.00, "Miscellaneous"),
        (26, "Food", 32.40, "Restaurant dinner"),
    ]

    for day, category, amount, description in sample_expenses:
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date_str, description),
        )

    conn.commit()
    conn.close()
