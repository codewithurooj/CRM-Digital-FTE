"""Unit tests for cross-channel identity resolution."""
import pytest
from unittest.mock import AsyncMock

from production.tests.conftest import make_mock_pool
from production.database.queries import customers


@pytest.mark.asyncio
async def test_resolve_by_email():
    """Test resolving a customer by email identifier."""
    pool, conn = make_mock_pool()
    # First query (identifier table) returns None, second (email) returns customer
    conn.fetchrow = AsyncMock(side_effect=[
        None,  # resolve_identity returns None
        {"id": "cust-1", "email": "alice@example.com", "name": "Alice"},  # get_customer_by_email
        None,  # create_identifier (ON CONFLICT DO NOTHING)
    ])

    result = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "web_form")

    assert result is not None
    assert result["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_resolve_by_phone_creates_new():
    """Test resolving unknown phone number creates new customer."""
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(side_effect=[
        None,  # resolve_identity returns None
        {"id": "cust-new", "email": "+1234567890@unknown.local", "phone": "+1234567890", "name": None},  # create_customer
        {"id": "ident-1"},  # create_identifier
    ])

    result = await customers.resolve_customer_identity(pool, "+1234567890", "phone", "whatsapp")

    assert result is not None
    assert result["id"] == "cust-new"


@pytest.mark.asyncio
async def test_resolve_existing_identifier():
    """Test resolving by existing identifier in customer_identifiers table."""
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(return_value={
        "id": "cust-1", "email": "alice@example.com", "name": "Alice",
    })

    result = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "email")

    assert result is not None
    assert result["id"] == "cust-1"


@pytest.mark.asyncio
async def test_create_identifier_prevents_duplicates():
    """Test that create_identifier uses ON CONFLICT DO NOTHING."""
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(return_value=None)  # ON CONFLICT returns None

    result = await customers.create_identifier(pool, "cust-1", "email", "alice@example.com", "web_form")

    # Should not raise even if duplicate
    assert result is None
    conn.fetchrow.assert_called_once()
