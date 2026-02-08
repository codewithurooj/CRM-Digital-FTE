"""Integration tests for guardrails — pricing/refund/legal messages trigger escalation."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from production.agent.customer_success_agent import process_message
from production.tests.conftest import make_mock_pool


@pytest.fixture
def mock_pool():
    pool, conn = make_mock_pool()
    # Mock ticket creation
    conn.fetchrow = AsyncMock(return_value={
        "id": "tkt-1", "ticket_number": "TKT-0001", "status": "open",
    })
    conn.execute = AsyncMock()
    return pool


def _patch_escalation_deps(pool):
    """Return a combined context manager that patches all _handle_escalation dependencies."""
    return [
        patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool),
        patch("production.database.queries.tickets.create_ticket", new_callable=AsyncMock, return_value={
            "id": "tkt-1", "ticket_number": "TKT-0001", "status": "open",
        }),
        patch("production.database.queries.tickets.update_ticket_status", new_callable=AsyncMock),
        patch("production.database.queries.conversations.update_status", new_callable=AsyncMock),
        patch("production.database.queries.messages.store_message", new_callable=AsyncMock),
        patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock),
    ]


@pytest.mark.asyncio
async def test_pricing_message_escalates(mock_pool):
    """Pricing question triggers immediate escalation."""
    patches = _patch_escalation_deps(mock_pool)
    for p in patches:
        p.start()
    try:
        result = await process_message(
            customer_id="cust-1",
            conversation_id="conv-1",
            channel="web_form",
            message="How much does the enterprise plan cost?",
            customer_name="Alice",
        )
        assert result["escalated"] is True
        assert "pricing" in result["reason"]
    finally:
        for p in patches:
            p.stop()


@pytest.mark.asyncio
async def test_refund_message_escalates(mock_pool):
    """Refund request triggers immediate escalation."""
    patches = _patch_escalation_deps(mock_pool)
    for p in patches:
        p.start()
    try:
        result = await process_message(
            customer_id="cust-1",
            conversation_id="conv-1",
            channel="email",
            message="I need a refund for last month's charge",
            customer_name="Bob",
        )
        assert result["escalated"] is True
        assert "refund" in result["reason"]
    finally:
        for p in patches:
            p.stop()


@pytest.mark.asyncio
async def test_legal_message_escalates(mock_pool):
    """Legal language triggers immediate escalation."""
    patches = _patch_escalation_deps(mock_pool)
    for p in patches:
        p.start()
    try:
        result = await process_message(
            customer_id="cust-1",
            conversation_id="conv-1",
            channel="email",
            message="I'm going to contact my lawyer about this",
            customer_name="Charlie",
        )
        assert result["escalated"] is True
        assert result["reason"] == "legal"
    finally:
        for p in patches:
            p.stop()


@pytest.mark.asyncio
async def test_human_request_escalates(mock_pool):
    """Explicit human request triggers escalation."""
    patches = _patch_escalation_deps(mock_pool)
    for p in patches:
        p.start()
    try:
        result = await process_message(
            customer_id="cust-1",
            conversation_id="conv-1",
            channel="whatsapp",
            message="human",
            customer_name="Dave",
        )
        assert result["escalated"] is True
    finally:
        for p in patches:
            p.stop()


@pytest.mark.asyncio
async def test_negative_sentiment_escalates(mock_pool):
    """Low sentiment score triggers escalation."""
    patches = _patch_escalation_deps(mock_pool)
    for p in patches:
        p.start()
    try:
        result = await process_message(
            customer_id="cust-1",
            conversation_id="conv-1",
            channel="web_form",
            message="I have a question about settings",
            customer_name="Eve",
            sentiment_score=0.1,
        )
        assert result["escalated"] is True
        assert result["reason"] == "negative_sentiment"
    finally:
        for p in patches:
            p.stop()
