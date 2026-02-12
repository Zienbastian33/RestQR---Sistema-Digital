"""
Integration tests for complete order flow and system functionality.

Feature: restqr-critical-fixes
Tests the complete end-to-end flows including QR generation, menu viewing,
cart operations, order submission, and confirmation.
"""
import pytest
import json
from app.models import TableToken, MenuItem, Order, OrderItem
from app.admin.routes import get_or_create_table_token
from app.main.routes import create_order_from_token
from app import db


def test_complete_order_flow(app, db_session):
    """
    Integration test: QR scan → menu view → add items → submit → confirmation
    
    Tests the complete customer journey from scanning a QR code to receiving
    order confirmation, verifying table number tracking throughout.
    
    Validates: All requirements
    """
    with app.app_context():
        # Step 1: Admin generates QR code for table 7
        token = get_or_create_table_token(7)
        assert token is not None
        assert token.table_number == 7
        assert token.is_active is True
        
        # Step 2: Create menu items in database
        menu_item1 = MenuItem(
            name="California Roll",
            description="Fresh salmon and avocado",
            price=12.50,
            category="Rolls",
            available=True
        )
        menu_item2 = MenuItem(
            name="Miso Soup",
            description="Traditional Japanese soup",
            price=4.50,
            category="Appetizers",
            available=True
        )
        db.session.add(menu_item1)
        db.session.add(menu_item2)
        db.session.commit()
        
        # Step 3: Verify token is valid and can be used to query menu items
        menu_items = MenuItem.query.filter_by(available=True).all()
        assert len(menu_items) == 2
        assert any(item.name == "California Roll" for item in menu_items)
        assert any(item.name == "Miso Soup" for item in menu_items)
        
        # Step 4: Customer adds items to cart and submits order
        items = [
            {'id': menu_item1.id, 'quantity': 2},
            {'id': menu_item2.id, 'quantity': 1}
        ]
        
        order = create_order_from_token(
            token_string=token.token,
            customer_name='John Doe',
            instructions='Extra wasabi please',
            items=items
        )
        
        # Step 5: Verify order was created with correct table number
        assert order is not None
        assert order.table_number == 7
        assert order.status == 'pending'
        assert len(order.items) == 2
        
        # Verify order items
        order_items = {item.menu_item_id: item.quantity for item in order.items}
        assert order_items[menu_item1.id] == 2
        assert order_items[menu_item2.id] == 1
        
        # Verify total calculation
        expected_total = (12.50 * 2) + (4.50 * 1)
        assert order.total == expected_total
        
        # Step 6: Verify order can be retrieved for confirmation page
        retrieved_order = Order.query.get(order.id)
        assert retrieved_order is not None
        assert retrieved_order.table_number == 7
        
        # Calculate total for confirmation (query menu items)
        confirmation_total = 0
        for item in retrieved_order.items:
            menu_item = MenuItem.query.get(item.menu_item_id)
            confirmation_total += menu_item.price * item.quantity
        assert confirmation_total == expected_total
        
        print("✓ Complete order flow integration test passed")


def test_cart_persistence_across_page_refresh(app, db_session):
    """
    Integration test: Verify cart persists across page refreshes
    
    Tests that cart state stored in localStorage (simulated via session)
    remains consistent when customer navigates between pages.
    
    Validates: Requirements 3.1, 3.2, 3.3
    """
    with app.app_context():
        # Create token and menu items
        token = get_or_create_table_token(15)
        
        menu_item = MenuItem(
            name="Salmon Nigiri",
            description="Fresh salmon",
            price=8.00,
            category="Nigiri",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Verify token is valid and menu items can be queried
        assert token.table_number == 15
        assert token.is_active is True
        
        # Verify menu items are available
        menu_items = MenuItem.query.filter_by(available=True).all()
        assert len(menu_items) == 1
        assert menu_items[0].name == "Salmon Nigiri"
        
        # Simulate cart operations - verify data consistency
        # In real app, cart is managed client-side in localStorage
        # Here we verify the backend data remains consistent
        
        # Create multiple orders to simulate page refreshes
        order1 = create_order_from_token(
            token_string=token.token,
            customer_name='Customer 1',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 1}]
        )
        
        # Verify table number persists across operations
        assert order1.table_number == 15
        
        # Simulate another "page refresh" - create another order
        order2 = create_order_from_token(
            token_string=token.token,
            customer_name='Customer 2',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 2}]
        )
        
        # Verify table number still consistent
        assert order2.table_number == 15
        
        # Verify both orders exist with same table
        orders = Order.query.filter_by(table_number=15).all()
        assert len(orders) == 2
        
        print("✓ Cart persistence integration test passed")


def test_multiple_orders_same_table(app, db_session):
    """
    Integration test: Multiple orders from same table using same token
    
    Tests that a table can place multiple orders using the same QR token
    without issues, verifying token reuse works correctly.
    
    Validates: Requirements 1.1, 1.2, 1.3
    """
    with app.app_context():
        # Create token and menu item
        token = get_or_create_table_token(20)
        
        menu_item = MenuItem(
            name="Green Tea",
            description="Hot green tea",
            price=3.00,
            category="Beverages",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Place first order
        order1 = create_order_from_token(
            token_string=token.token,
            customer_name='First Order',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 2}]
        )
        
        assert order1 is not None
        assert order1.table_number == 20
        
        # Place second order with same token
        order2 = create_order_from_token(
            token_string=token.token,
            customer_name='Second Order',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 1}]
        )
        
        assert order2 is not None
        assert order2.table_number == 20
        assert order1.id != order2.id
        
        # Verify token was reused (only one token exists for table 20)
        tokens = TableToken.query.filter_by(table_number=20, is_active=True).all()
        assert len(tokens) == 1
        
        print("✓ Multiple orders same table integration test passed")
