"""
Integration tests for admin QR generation and token management.

Feature: restqr-critical-fixes
Tests admin functionality including QR code generation, token reuse,
and table management.
"""
import pytest
import json
import base64
from app.models import TableToken
from app.admin.routes import get_or_create_table_token
from app import db


def test_qr_generation_reuses_existing_tokens(app, db_session):
    """
    Integration test: QR generation reuses existing tokens
    
    Tests that generating QR codes multiple times for the same table
    returns the same token, preventing unnecessary QR code reprints.
    
    Validates: Requirements 1.1, 1.2, 1.3
    """
    with app.app_context():
        # Generate token for table 10 (first time)
        token1 = get_or_create_table_token(10)
        
        assert token1 is not None
        assert token1.table_number == 10
        assert token1.is_active is True
        assert token1.token is not None
        
        # Generate token for table 10 again (second time)
        token2 = get_or_create_table_token(10)
        
        # Verify same token is returned
        assert token1.id == token2.id, "Token should be reused for same table"
        assert token1.token == token2.token, "Token string should be identical"
        
        # Generate token for table 10 a third time
        token3 = get_or_create_table_token(10)
        
        assert token1.id == token3.id, "Token should still be reused"
        
        # Verify only one active token exists in database
        active_tokens = TableToken.query.filter_by(
            table_number=10,
            is_active=True
        ).all()
        
        assert len(active_tokens) == 1, "Should have exactly one active token"
        assert active_tokens[0].token == token1.token
        
        print("✓ QR generation token reuse integration test passed")


def test_qr_generation_different_tables(app, db_session):
    """
    Integration test: Different tables get different tokens
    
    Tests that generating QR codes for different tables creates
    unique tokens for each table.
    
    Validates: Requirements 1.1, 1.5
    """
    with app.app_context():
        # Generate tokens for multiple tables
        tables = [3, 7, 15, 22]
        tokens = {}
        
        for table_num in tables:
            token = get_or_create_table_token(table_num)
            tokens[table_num] = token.token
        
        # Verify all tokens are unique
        token_values = list(tokens.values())
        assert len(token_values) == len(set(token_values)), "All tokens should be unique"
        
        # Verify each token has correct table number
        for table_num, token_str in tokens.items():
            token = TableToken.query.filter_by(token=token_str).first()
            assert token is not None
            assert token.table_number == table_num
            assert token.is_active is True
        
        print("✓ Different tables different tokens integration test passed")


def test_table_activation_workflow(app, db_session):
    """
    Integration test: Complete table activation workflow
    
    Tests the full workflow of generating a QR code, activating the table
    with an activation code, and verifying the session is active.
    
    Validates: Requirements 1.1, 1.4
    """
    with app.app_context():
        # Step 1: Generate token for table
        token = get_or_create_table_token(25)
        
        assert token is not None
        assert token.table_number == 25
        assert token.is_active is True
        assert token.session_active is False  # Not yet activated
        assert token.activation_code is not None
        assert len(token.activation_code) == 6
        
        # Step 2: Simulate activation
        token.session_active = True
        from datetime import datetime, timedelta
        token.session_start = datetime.utcnow()
        token.session_end = datetime.utcnow() + timedelta(hours=2)
        db.session.commit()
        
        # Step 3: Verify session is now active
        activated_token = TableToken.query.filter_by(token=token.token).first()
        assert activated_token.session_active is True
        assert activated_token.session_start is not None
        assert activated_token.session_end is not None
        
        print("✓ Table activation workflow integration test passed")


def test_table_deactivation_workflow(app, db_session):
    """
    Integration test: Table deactivation workflow
    
    Tests that tables can be deactivated after service, ending the session.
    
    Validates: Requirements 6.3
    """
    with app.app_context():
        # Create and activate a table
        token = get_or_create_table_token(30)
        
        # Activate the session
        from datetime import datetime, timedelta
        token.session_active = True
        token.session_start = datetime.utcnow()
        token.session_end = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # Verify table is active
        assert token.session_active is True
        
        # Deactivate the table
        token.session_active = False
        token.session_end = datetime.utcnow()
        db.session.commit()
        
        # Verify table is now inactive
        deactivated_token = TableToken.query.filter_by(token=token.token).first()
        assert deactivated_token.session_active is False
        
        print("✓ Table deactivation workflow integration test passed")


def test_active_tables_listing(app, db_session):
    """
    Integration test: Active tables listing
    
    Tests that the admin can view all currently active tables.
    
    Validates: Requirements 6.3
    """
    with app.app_context():
        # Create and activate multiple tables
        tables_to_activate = [5, 10, 15]
        
        from datetime import datetime, timedelta
        for table_num in tables_to_activate:
            token = get_or_create_table_token(table_num)
            token.session_active = True
            token.session_start = datetime.utcnow()
            token.session_end = datetime.utcnow() + timedelta(hours=2)
            db.session.commit()
        
        # Query active tables
        active_tables = TableToken.query.filter_by(session_active=True).all()
        active_table_numbers = [t.table_number for t in active_tables 
                               if t.session_end and t.session_end > datetime.utcnow()]
        
        # Verify all activated tables appear in the list
        for table_num in tables_to_activate:
            assert table_num in active_table_numbers
        
        print("✓ Active tables listing integration test passed")


def test_token_uniqueness_constraint(app, db_session):
    """
    Integration test: Token uniqueness is enforced
    
    Tests that the system prevents duplicate active tokens for the same table.
    
    Validates: Requirements 1.5, 7.3
    """
    with app.app_context():
        # Create token for table 40
        token1 = get_or_create_table_token(40)
        
        # Try to create another token for same table
        token2 = get_or_create_table_token(40)
        
        # Should return the same token
        assert token1.id == token2.id
        
        # Verify only one active token exists
        active_tokens = TableToken.query.filter_by(
            table_number=40,
            is_active=True
        ).all()
        
        assert len(active_tokens) == 1
        
        print("✓ Token uniqueness constraint integration test passed")
