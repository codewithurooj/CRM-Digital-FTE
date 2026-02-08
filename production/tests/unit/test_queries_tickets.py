"""Unit tests for ticket queries — T016 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestTicketQueries:

    @pytest.mark.asyncio
    async def test_create_ticket(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={
            "id": "t-1", "ticket_number": "TKT-0001", "subject": "Help", "status": "open"
        })
        from production.database.queries.tickets import create_ticket
        result = await create_ticket(pool, "c-1", "Help", "how_to", "web_form")
        assert result["ticket_number"] == "TKT-0001"
        assert result["status"] == "open"

    @pytest.mark.asyncio
    async def test_get_ticket_by_number(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"ticket_number": "TKT-0001"})
        from production.database.queries.tickets import get_ticket_by_number
        result = await get_ticket_by_number(pool, "TKT-0001")
        assert result["ticket_number"] == "TKT-0001"

    @pytest.mark.asyncio
    async def test_update_ticket_status(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "t-1", "status": "escalated"})
        from production.database.queries.tickets import update_ticket_status
        result = await update_ticket_status(pool, "t-1", "escalated", escalation_reason="pricing")
        assert result["status"] == "escalated"
