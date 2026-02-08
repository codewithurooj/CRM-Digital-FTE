"""E2E test for Gmail flow — Pub/Sub notification → Kafka → agent → email reply."""
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

            yield application, producer


@pytest.mark.asyncio
async def test_gmail_e2e_pubsub_to_kafka(app):
    """Gmail Pub/Sub notification → published to Kafka."""
    application, producer = app

    data = base64.b64encode(json.dumps({
        "emailAddress": "customer@example.com",
        "historyId": 99999,
    }).encode()).decode()

    payload = {
        "message": {"data": data, "messageId": "pubsub-msg-1"},
        "subscription": "projects/techcorp/subscriptions/gmail-push",
    }

    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as client:
        response = await client.post("/api/v1/webhooks/gmail", json=payload)

    assert response.status_code == 200
    producer.send_and_wait.assert_called_once()

    # Verify message published to correct topic
    call_args = producer.send_and_wait.call_args
    assert call_args[0][0] == "fte.tickets.incoming"

    # Verify message content
    published = json.loads(call_args[0][1].decode("utf-8"))
    assert published["customer_identifier"] == "customer@example.com"
    assert published["channel"] == "email"
