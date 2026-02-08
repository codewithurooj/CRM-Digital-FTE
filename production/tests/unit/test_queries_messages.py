"""Unit tests for message queries — T015 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestMessageQueries:

    @pytest.mark.asyncio
    async def test_store_message(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "msg-1", "content": "Hello"})
        from production.database.queries.messages import store_message
        result = await store_message(pool, "conv-1", "cust-1", "web_form", "inbound", "customer", "Hello")
        assert result["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_get_messages_by_conversation(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[{"id": "msg-1"}, {"id": "msg-2"}])
        from production.database.queries.messages import get_messages_by_conversation
        result = await get_messages_by_conversation(pool, "conv-1")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_customer_history(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[{"id": "msg-1", "conv_channel": "email"}])
        from production.database.queries.messages import get_customer_history
        result = await get_customer_history(pool, "cust-1")
        assert result[0]["conv_channel"] == "email"
