"""Unit tests for conversation queries — T014 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestConversationQueries:

    @pytest.mark.asyncio
    async def test_create_conversation(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "conv-1", "customer_id": "c-1", "channel": "web_form"})
        from production.database.queries.conversations import create_conversation
        result = await create_conversation(pool, "c-1", "web_form")
        assert result["channel"] == "web_form"

    @pytest.mark.asyncio
    async def test_update_status(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "conv-1", "status": "escalated"})
        from production.database.queries.conversations import update_status
        result = await update_status(pool, "conv-1", "escalated", escalation_reason="pricing")
        assert result["status"] == "escalated"

    @pytest.mark.asyncio
    async def test_get_active_by_customer(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[{"id": "conv-1", "status": "active"}])
        from production.database.queries.conversations import get_active_by_customer
        result = await get_active_by_customer(pool, "c-1")
        assert len(result) == 1
