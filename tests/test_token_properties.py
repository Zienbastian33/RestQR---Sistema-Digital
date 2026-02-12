"""
Property-based tests for QR code token management.

Feature: restqr-critical-fixes
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models import TableToken
from app.admin.routes import get_or_create_table_token
from app import db


# Feature: restqr-critical-fixes, Property 3: Active token uniqueness
@given(table_number=st.integers(min_value=1, max_value=100))
@settings(
    max_examples=100, 
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_active_token_uniqueness(app, db_session, table_number):
    """
    Property 3: Active token uniqueness
    
    For any table number at any point in time, there should be at most 
    one active token associated with that table number in the database.
    
    Validates: Requirements 1.5
    """
    with app.app_context():
        # Clean up any existing tokens for this table from previous examples
        TableToken.query.filter_by(table_number=table_number).delete()
        db.session.commit()
        
        # Create multiple tokens for the same table
        token1 = get_or_create_table_token(table_number)
        token2 = get_or_create_table_token(table_number)
        token3 = get_or_create_table_token(table_number)
        
        # Query all active tokens for this table number
        active_tokens = TableToken.query.filter_by(
            table_number=table_number,
            is_active=True
        ).all()
        
        # Assert: There should be exactly one active token
        assert len(active_tokens) == 1, \
            f"Expected exactly 1 active token for table {table_number}, found {len(active_tokens)}"
        
        # Assert: All get_or_create calls should return the same token
        assert token1.id == token2.id == token3.id, \
            f"Multiple calls should return same token ID"
        
        assert token1.token == token2.token == token3.token, \
            f"Multiple calls should return same token string"
        
        # Verify the single active token has correct table number
        assert active_tokens[0].table_number == table_number, \
            f"Active token should have correct table number"
        
        assert active_tokens[0].is_active is True, \
            f"Active token should have is_active=True"
