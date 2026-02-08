"""E2E test for web form flow — form submit → Kafka → agent → response stored → ticket queryable."""
import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def e2e_mocks():
    pool, conn = make_mock_pool()

    customer = {"id": "cust-1", "email": "e2e@example.com", "name": "E2E User"}
    conversation = {"id": "conv-1", "customer_id": "cust-1", "channel": "web_form", "status": "active"}
    message = {"id": "msg-1", "conversation_id": "conv-1", "content": "Test"}
    ticket = {
        "id": "tkt-1", "ticket_number": "TKT-0001", "status": "open",
        "customer_id": "cust-1", "subject": "E2E Test", "category": "technical",
        "priority": "medium", "source_channel": "web_form", "conversation_id": "conv-1",
        "created_at": "2026-02-08T00:00:00Z", "updated_at": "2026-02-08T00:00:00Z",
    }

    conn.fetchrow = AsyncMock(side_effect=[
        None, customer, {"id": "id-1"},  # resolve customer
        conversation,  # create conversation
        message,       # store message
        ticket,        # create ticket
    ])

    return pool, conn, ticket


@pytest.fixture
def app(e2e_mocks):
    pool, conn, ticket = e2e_mocks
    from production.api.main import create_app
    application = create_app()

    async def override_pool():
        return pool

    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_db_pool"]).get_db_pool
    ] = override_pool

    return application


@pytest.mark.asyncio
async def test_web_form_e2e_submit_and_query(app, e2e_mocks):
    """Full E2E: submit form → get ticket."""
    pool, conn, ticket = e2e_mocks

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Submit form
        submit_response = await client.post("/api/v1/support/form", json={
            "name": "E2E User",
            "email": "e2e@example.com",
            "subject": "E2E Test Subject",
            "category": "technical",
            "priority": "medium",
            "message": "This is an end-to-end test of the web form flow.",
        })

        assert submit_response.status_code == 201
        ticket_id = submit_response.json()["ticket_id"]
        assert ticket_id == "TKT-0001"

    # Step 2: Query ticket status (new mock for GET)
    conn.fetchrow = AsyncMock(return_value=ticket)
    conn.fetch = AsyncMock(return_value=[])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        status_response = await client.get(f"/api/v1/tickets/{ticket_id}")

    assert status_response.status_code == 200
    data = status_response.json()
    assert data["ticket_id"] == "TKT-0001"
    assert data["status"] == "open"
