"""E2E test for cross-channel flow — customer via web form then email → single record."""
import pytest
from unittest.mock import AsyncMock

from production.tests.conftest import make_mock_pool
from production.database.queries import customers, messages


@pytest.mark.asyncio
async def test_cross_channel_same_customer():
    """Customer contacts via web form and email — recognized as same person."""
    pool, conn = make_mock_pool()
    customer = {"id": "cust-1", "email": "alice@example.com", "name": "Alice"}

    # Web form: resolve → create new → link identifier
    conn.fetchrow = AsyncMock(side_effect=[
        None,                # resolve_identity not found
        None,                # get_customer_by_email not found
        customer,            # create_customer
        {"id": "ident-1"},   # create_identifier
    ])

    result1 = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "web_form")
    assert result1["id"] == "cust-1"

    # Email: resolve → found via identifier
    conn.fetchrow = AsyncMock(return_value=customer)

    result2 = await customers.resolve_customer_identity(pool, "alice@example.com", "email", "email")
    assert result2["id"] == "cust-1"

    # Same customer ID
    assert result1["id"] == result2["id"]


@pytest.mark.asyncio
async def test_cross_channel_full_history():
    """Full history includes messages from all channels."""
    pool, conn = make_mock_pool()
    conn.fetch = AsyncMock(return_value=[
        {"id": "m1", "content": "Web form msg", "channel": "web_form", "conv_channel": "web_form",
         "direction": "inbound", "role": "customer", "created_at": "2026-02-08T01:00:00Z"},
        {"id": "m2", "content": "Email msg", "channel": "email", "conv_channel": "email",
         "direction": "inbound", "role": "customer", "created_at": "2026-02-08T02:00:00Z"},
        {"id": "m3", "content": "WhatsApp msg", "channel": "whatsapp", "conv_channel": "whatsapp",
         "direction": "inbound", "role": "customer", "created_at": "2026-02-08T03:00:00Z"},
    ])

    history = await messages.get_full_customer_history(pool, "cust-1")

    assert len(history) == 3
    channels = {m["channel"] for m in history}
    assert channels == {"web_form", "email", "whatsapp"}
