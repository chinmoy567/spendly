"""Pytest configuration and shared fixtures."""

import pytest
import os
import tempfile
from app import app
from database.db import init_db, get_db


@pytest.fixture
def test_db():
    """Create a test database in a temporary file."""
    db_fd, db_path = tempfile.mkstemp()

    # Override the database path for testing
    original_db_path = os.environ.get('DB_PATH')
    os.environ['DB_PATH'] = db_path

    yield db_path

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    if original_db_path:
        os.environ['DB_PATH'] = original_db_path
    else:
        os.environ.pop('DB_PATH', None)


@pytest.fixture
def app_instance():
    """Create and configure a test app instance."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app
