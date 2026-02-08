"""Integration tests for cross-channel customer identity resolution."""
import pytest
from unittest.mock import AsyncMock

from production.tests.conftest import make_mock_pool
from production.database.queries import customers


@pytest.mark.asyncio
async def test_web_then_email_same_customer():
    """Customer submits web form, then emails — same record."""
    pool, conn = make_mock_pool()

    customer_record = {"id": "cust-1", "email": "alice@example.com", "name": "Alice"}

    # First call: web form submission
    conn.fetchrow = AsyncMock(side_effect=[
        None,                # resolve_identity → not found
        customer_record,     # get_customer_by_email → found
        {"id": "ident-1"},   # create_identifier
    ])

    result1 = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "web_form")
    assert result1["id"] == "cust-1"

    # Second call: email from same address
    conn.fetchrow = AsyncMock(return_value=customer_record)

    result2 = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "email")
    assert result2["id"] == "cust-1"

    # Same customer
    assert result1["id"] == result2["id"]


@pytest.mark.asyncio
async def test_new_phone_creates_new_customer():
    """New WhatsApp phone number creates new customer."""
    pool, conn = make_mock_pool()

    new_customer = {"id": "cust-new", "email": "+1234567890@unknown.local", "phone": "+1234567890", "name": None}

    conn.fetchrow = AsyncMock(side_effect=[
        None,           # resolve_identity → not found
        new_customer,   # create_customer
        {"id": "id-1"}, # create_identifier
    ])

    result = await customers.resolve_customer_identity(pool, "+1234567890", "phone", "whatsapp")
    assert result is not None
    assert result["id"] == "cust-new"
