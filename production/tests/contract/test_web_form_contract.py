"""Contract test for POST /api/v1/support/form — T029 TDD target."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from production.tests.conftest import make_mock_pool


@pytest.fixture
def valid_form_data():
    return {
        "name": "Lisa Chen",
        "email": "lisa.chen@example.com",
        "subject": "How to set up automations?",
        "category": "how_to",
        "priority": "medium",
        "message": "I want to set up a Slack automation. Can you help me with the steps?",
    }


@pytest.fixture
def mock_deps():
    pool, conn = make_mock_pool()
    conn.fetchrow = AsyncMock(return_value=None)  # no existing customer
    # For create_customer
    conn.fetchrow.side_effect = [
        None,  # get_customer_by_email -> not found
        {"id": "cust-1", "email": "lisa.chen@example.com", "name": "Lisa Chen"},  # create_customer
        {"id": "ci-1"},  # create_identifier
        {"id": "conv-1", "customer_id": "cust-1", "channel": "web_form"},  # create_conversation
        {"id": "msg-1"},  # store_message
        {"id": "t-1", "ticket_number": "TKT-0001", "status": "open",  # create_ticket
         "subject": "How to set up automations?", "category": "how_to",
         "priority": "medium", "source_channel": "web_form",
         "created_at": "2026-02-08T12:00:00Z", "updated_at": "2026-02-08T12:00:00Z"},
    ]
    return pool


@pytest.fixture
def app(mock_deps):
    """Create app with mocked DB pool (including lifespan)."""
    from production.api.dependencies import get_db_pool, get_kafka_producer

    with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=mock_deps):
        with patch("production.database.pool.close_pool", new_callable=AsyncMock):
            from production.api.main import create_app
            application = create_app()

            async def override_pool():
                return mock_deps

            async def override_producer():
                producer = AsyncMock()
                producer.send_and_wait = AsyncMock()
                return producer

            application.dependency_overrides[get_db_pool] = override_pool
            application.dependency_overrides[get_kafka_producer] = override_producer

            yield application


class TestWebFormContract:

    @pytest.mark.asyncio
    async def test_201_valid_submission(self, valid_form_data, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/support/form", json=valid_form_data)
            assert resp.status_code == 201
            body = resp.json()
            assert "ticket_id" in body
            assert body["status"] == "received"
            assert "created_at" in body

    @pytest.mark.asyncio
    async def test_400_missing_email(self, valid_form_data, app):
        del valid_form_data["email"]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/support/form", json=valid_form_data)
            assert resp.status_code == 400 or resp.status_code == 422

    @pytest.mark.asyncio
    async def test_400_short_message(self, valid_form_data, app):
        valid_form_data["message"] = "Hi"  # less than 10 chars
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/support/form", json=valid_form_data)
            assert resp.status_code == 400 or resp.status_code == 422

    @pytest.mark.asyncio
    async def test_400_invalid_category(self, valid_form_data, app):
        valid_form_data["category"] = "invalid_cat"
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/support/form", json=valid_form_data)
            assert resp.status_code == 400 or resp.status_code == 422
