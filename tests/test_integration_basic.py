"""
Basic integration tests for token and order tracking.
"""
import pytest
from app.models import TableToken, Order, MenuItem, OrderItem
from app.admin.routes import get_or_create_table_token
from app.main.routes import create_order_from_token
from app import db


def test_token_creation_and_reuse(app, db_session):
    """Test that tokens are created and reused correctly."""
    with app.app_context():
        # Create a token for table 5
        token1 = get_or_create_table_token(5)
        assert token1 is not None
        assert token1.table_number == 5
        assert token1.is_active is True
        
        # Try to create another token for the same table
        token2 = get_or_create_table_token(5)
        assert token2.id == token1.id
        assert token2.token == token1.token
        
        print("✓ Token creation and reuse works correctly")


def test_order_creation_with_table_number(app, db_session):
    """Test that orders are created with table numbers from tokens."""
    with app.app_context():
        # Create a token for table 10
        token = get_or_create_table_token(10)
        
        # Create a menu item for testing
        menu_item = MenuItem(
            name="Test Sushi",
            description="Test item",
            price=10.0,
            category="Test",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Create an order using the token
        items = [{'id': menu_item.id, 'quantity': 2}]
        order = create_order_from_token(
            token_string=token.token,
            customer_name="Test Customer",
            instructions="No wasabi",
            items=items
        )
        
        assert order is not None
        assert order.table_number == 10
        assert order.status == 'pending'
        assert len(order.items) == 1
        assert order.items[0].quantity == 2
        
        print("✓ Order creation with table number works correctly")


def test_order_creation_with_invalid_token(app, db_session):
    """Test that orders fail with invalid tokens."""
    with app.app_context():
        # Try to create an order with a non-existent token
        order = create_order_from_token(
            token_string="invalid_token_12345",
            customer_name="Test Customer",
            instructions="",
            items=[{'id': 1, 'quantity': 1}]
        )
        
        assert order is None
        print("✓ Invalid token rejection works correctly")


def test_inactive_token_rejection(app, db_session):
    """Test that orders fail when token is inactive."""
    with app.app_context():
        # Create an inactive token
        inactive_token = TableToken(
            token="inactive_token_123",
            table_number=15,
            is_active=False
        )
        db.session.add(inactive_token)
        db.session.commit()
        
        # Try to create an order with this token
        order = create_order_from_token(
            token_string=inactive_token.token,
            customer_name="Test Customer",
            instructions="",
            items=[{'id': 1, 'quantity': 1}]
        )
        
        assert order is None
        print("✓ Inactive token rejection works correctly")
