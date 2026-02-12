"""
Test configuration and fixtures for RestQR tests.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import TableToken, MenuItem, Order, OrderItem
from config import Config


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    # Use use_cookies=False to avoid as_tuple parameter issue
    with app.test_client(use_cookies=False) as client:
        yield client


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for tests."""
    with app.app_context():
        yield db.session
