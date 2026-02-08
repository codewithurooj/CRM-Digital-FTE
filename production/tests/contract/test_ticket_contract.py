"""Contract test for GET /api/v1/tickets/{ticket_id} — T030 TDD target."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app_with_ticket():
    """Create app with mocked DB pool that returns a ticket."""
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(return_value={
        "id": "uuid-1", "ticket_number": "TKT-0001", "status": "open",
        "category": "how_to", "priority": "medium",
        "subject": "How to set up automations?",
        "source_channel": "web_form",
        "created_at": "2026-02-08T12:00:00+00:00",
        "updated_at": "2026-02-08T12:00:00+00:00",
        "resolved_at": None,
    })
    conn.fetch = AsyncMock(return_value=[])  # no responses yet

    from production.api.dependencies import get_db_pool

    with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool):
        with patch("production.database.pool.close_pool", new_callable=AsyncMock):
            from production.api.main import create_app
            application = create_app()

            async def override_pool():
                return pool

            application.dependency_overrides[get_db_pool] = override_pool
            yield application


@pytest.fixture
def app_no_ticket():
    """Create app with mocked DB pool that returns no ticket."""
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(return_value=None)

    from production.api.dependencies import get_db_pool

    with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool):
        with patch("production.database.pool.close_pool", new_callable=AsyncMock):
            from production.api.main import create_app
            application = create_app()

            async def override_pool():
                return pool

            application.dependency_overrides[get_db_pool] = override_pool
            yield application


class TestTicketContract:

    @pytest.mark.asyncio
    async def test_200_ticket_found(self, app_with_ticket):
        transport = ASGITransport(app=app_with_ticket)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/tickets/TKT-0001")
            assert resp.status_code == 200
            body = resp.json()
            assert body["ticket_id"] == "TKT-0001"
            assert body["status"] == "open"
            assert "created_at" in body

    @pytest.mark.asyncio
    async def test_404_ticket_not_found(self, app_no_ticket):
        transport = ASGITransport(app=app_no_ticket)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/tickets/TKT-9999")
            assert resp.status_code == 404
