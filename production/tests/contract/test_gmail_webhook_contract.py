"""Contract tests for POST /api/v1/webhooks/gmail — Pub/Sub payload, auth."""
import base64
import json
import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app():
    pool, conn = make_mock_pool()
    producer = AsyncMock()
    producer.send_and_wait = AsyncMock()

    from production.api.dependencies import get_db_pool, get_kafka_producer

    with patch("production.database.pool.get_pool", new_callable=AsyncMock, return_value=pool):
        with patch("production.database.pool.close_pool", new_callable=AsyncMock):
            from production.api.main import create_app
            application = create_app()

            async def override_pool():
                return pool

            async def override_producer():
                return producer

            application.dependency_overrides[get_db_pool] = override_pool
            application.dependency_overrides[get_kafka_producer] = override_producer

            yield application


@pytest.mark.asyncio
async def test_gmail_webhook_accepts_valid_pubsub(app):
    """Valid Pub/Sub notification returns 200."""
    data = base64.b64encode(json.dumps({
        "emailAddress": "customer@example.com",
        "historyId": 12345,
    }).encode()).decode()

    payload = {
        "message": {"data": data, "messageId": "pub123"},
        "subscription": "projects/test/subscriptions/gmail",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/webhooks/gmail", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_gmail_webhook_rejects_invalid_payload(app):
    """Invalid payload returns 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/gmail",
            content="not json",
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code in (400, 422)
