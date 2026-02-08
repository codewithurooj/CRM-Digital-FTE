"""Integration test for web form submission flow — submit → ticket created → response."""
import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app():
    pool, conn = make_mock_pool()

    # Mock customer lookup → None (new customer), then create
    customer_record = {"id": "cust-1", "email": "lisa@example.com", "name": "Lisa Chen"}
    conversation_record = {"id": "conv-1", "customer_id": "cust-1", "channel": "web_form"}
    message_record = {"id": "msg-1", "conversation_id": "conv-1", "content": "Help"}
    ticket_record = {
        "id": "tkt-1", "ticket_number": "TKT-0001", "status": "open",
        "customer_id": "cust-1", "subject": "Automation help", "category": "how_to",
        "priority": "medium", "source_channel": "web_form", "conversation_id": "conv-1",
        "created_at": "2026-02-08T00:00:00Z", "updated_at": "2026-02-08T00:00:00Z",
    }

    conn.fetchrow = AsyncMock(side_effect=[
        None,               # get_customer_by_email → not found
        customer_record,    # create_customer
        {"id": "ident-1"},  # create_identifier
        conversation_record,  # create_conversation
        message_record,     # store_message
        ticket_record,      # create_ticket
    ])

    from production.api.main import create_app
    application = create_app()

    async def override_pool():
        return pool

    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_db_pool"]).get_db_pool
    ] = override_pool

    return application


@pytest.mark.asyncio
async def test_submit_form_creates_ticket(app):
    """Submit form → ticket created → response has ticket_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/support/form", json={
            "name": "Lisa Chen",
            "email": "lisa@example.com",
            "subject": "How to set up automations?",
            "category": "how_to",
            "priority": "medium",
            "message": "I just upgraded to Starter and I am trying to set up an automation.",
        })

    assert response.status_code == 201
    data = response.json()
    assert "ticket_id" in data
    assert data["ticket_id"] == "TKT-0001"
    assert data["status"] == "received"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_submit_form_validation_error(app):
    """Invalid form data returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/support/form", json={
            "name": "L",
            "email": "not-an-email",
            "subject": "Hi",
            "category": "how_to",
            "message": "short",
        })

    assert response.status_code == 422
