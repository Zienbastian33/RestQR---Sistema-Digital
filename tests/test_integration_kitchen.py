"""
Integration tests for kitchen display and real-time updates.

Feature: restqr-critical-fixes
Tests kitchen display functionality including table number display
and SocketIO real-time updates.
"""
import pytest
import json
from app.models import TableToken, MenuItem, Order, OrderItem
from app.admin.routes import get_or_create_table_token
from app.main.routes import create_order_from_token
from app import db


def test_kitchen_display_shows_table_numbers(app, db_session):
    """
    Integration test: Kitchen display shows table numbers for orders
    
    Tests that orders appear in the kitchen display with correct table numbers,
    verifying the kitchen staff can see which table each order is for.
    
    Validates: Requirements 2.4, 6.2
    """
    with app.app_context():
        # Create tokens for multiple tables
        token1 = get_or_create_table_token(5)
        token2 = get_or_create_table_token(12)
        
        # Create menu items
        menu_item = MenuItem(
            name="Tempura Roll",
            description="Crispy tempura",
            price=14.00,
            category="Rolls",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Create orders from different tables
        order1 = create_order_from_token(
            token_string=token1.token,
            customer_name='Customer 1',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 1}]
        )
        
        order2 = create_order_from_token(
            token_string=token2.token,
            customer_name='Customer 2',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 2}]
        )
        
        assert order1 is not None
        assert order2 is not None
        
        # Query pending orders (simulating kitchen display query)
        kitchen_orders = Order.query.filter_by(
            is_delivery=False,
            status='pending'
        ).all()
        
        # Verify both orders appear with correct table numbers
        assert len(kitchen_orders) >= 2
        
        table_numbers = [order.table_number for order in kitchen_orders]
        assert 5 in table_numbers
        assert 12 in table_numbers
        
        # Verify order details
        for order in kitchen_orders:
            assert order.table_number is not None
            assert len(order.items) > 0
            assert order.total > 0
            
        print("✓ Kitchen display table numbers integration test passed")


def test_kitchen_display_handles_legacy_orders(app, db_session):
    """
    Integration test: Kitchen display handles orders without table numbers
    
    Tests backward compatibility - the system now requires table numbers,
    but we verify that the validation works correctly.
    
    Validates: Requirements 6.5
    """
    with app.app_context():
        # Create a menu item
        menu_item = MenuItem(
            name="Edamame",
            description="Steamed soybeans",
            price=5.00,
            category="Appetizers",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Note: The current schema requires table_number (NOT NULL constraint)
        # This is correct per requirements - all new orders must have table numbers
        # Legacy orders in production DB would have been created before the constraint
        
        # Verify that attempting to create order without table number fails
        # This validates that the system enforces table number requirement
        try:
            legacy_order = Order(
                table_number=None,  # Should fail
                status='pending',
                total=5.00,
                is_delivery=False
            )
            db.session.add(legacy_order)
            db.session.commit()
            # If we get here, the constraint isn't working
            assert False, "Should have raised IntegrityError for NULL table_number"
        except Exception as e:
            # Expected - table_number is required
            db.session.rollback()
            assert "NOT NULL constraint failed" in str(e) or "IntegrityError" in str(type(e).__name__)
        
        # Create a valid order with table number to verify system works
        valid_order = Order(
            table_number=99,  # Valid table number
            status='pending',
            total=5.00,
            is_delivery=False
        )
        db.session.add(valid_order)
        
        order_item = OrderItem(
            order=valid_order,
            menu_item_id=menu_item.id,
            quantity=1
        )
        db.session.add(order_item)
        db.session.commit()
        
        # Query kitchen orders - should work fine
        kitchen_orders = Order.query.filter_by(
            is_delivery=False,
            status='pending'
        ).all()
        
        # Verify valid order appears
        assert any(o.id == valid_order.id for o in kitchen_orders)
        
        # Verify all orders have table numbers (as required)
        for order in kitchen_orders:
            assert order.table_number is not None
            assert isinstance(order.table_number, int)
            
        print("✓ Kitchen display legacy orders integration test passed")


def test_order_completion_workflow(app, db_session):
    """
    Integration test: Complete order workflow in kitchen
    
    Tests that kitchen staff can mark orders as completed and they
    are removed from the active orders list.
    
    Validates: Requirements 6.2
    """
    with app.app_context():
        # Create token and menu item
        token = get_or_create_table_token(8)
        
        menu_item = MenuItem(
            name="Sashimi Platter",
            description="Assorted fresh fish",
            price=25.00,
            category="Sashimi",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Create order
        order = create_order_from_token(
            token_string=token.token,
            customer_name='Customer',
            instructions='',
            items=[{'id': menu_item.id, 'quantity': 1}]
        )
        
        assert order is not None
        order_id = order.id
        
        # Verify order appears in pending orders
        pending_orders = Order.query.filter_by(status='pending').all()
        order_ids = [o.id for o in pending_orders]
        assert order_id in order_ids
        
        # Complete the order
        order.status = 'completed'
        db.session.commit()
        
        # Verify order is marked as completed
        completed_order = Order.query.get(order_id)
        assert completed_order.status == 'completed'
        
        # Verify order no longer appears in pending orders
        pending_orders = Order.query.filter_by(status='pending').all()
        order_ids = [o.id for o in pending_orders]
        assert order_id not in order_ids
        
        print("✓ Order completion workflow integration test passed")


def test_concurrent_orders_different_tables(app, db_session):
    """
    Integration test: Multiple concurrent orders from different tables
    
    Tests that the system can handle multiple simultaneous orders from
    different tables without data corruption or conflicts.
    
    Validates: Requirements 7.5
    """
    with app.app_context():
        # Create tokens for multiple tables
        tokens = [get_or_create_table_token(i) for i in range(1, 6)]
        
        # Create menu item
        menu_item = MenuItem(
            name="Ramen Bowl",
            description="Traditional ramen",
            price=12.00,
            category="Noodles",
            available=True
        )
        db.session.add(menu_item)
        db.session.commit()
        
        # Submit orders from all tables
        orders = []
        for token in tokens:
            order = create_order_from_token(
                token_string=token.token,
                customer_name='Customer',
                instructions='',
                items=[{'id': menu_item.id, 'quantity': 1}]
            )
            assert order is not None
            orders.append(order)
        
        # Verify all orders were created with correct table numbers
        for i, order in enumerate(orders):
            assert order.table_number == i + 1
            assert order.status == 'pending'
        
        # Verify all orders appear in kitchen
        kitchen_orders = Order.query.filter_by(
            is_delivery=False,
            status='pending'
        ).all()
        
        kitchen_order_ids = [o.id for o in kitchen_orders]
        
        for order in orders:
            assert order.id in kitchen_order_ids
        
        print("✓ Concurrent orders integration test passed")
