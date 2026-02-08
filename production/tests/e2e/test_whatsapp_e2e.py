"""E2E test for WhatsApp flow — Twilio webhook → Kafka → agent → WhatsApp reply."""
import json
import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app():
    pool, conn = make_mock_pool()
    producer = AsyncMock()
    producer.send_and_wait = AsyncMock()

    from production.api.main import create_app
    application = create_app()

    async def override_pool():
        return pool

    async def override_producer():
        return producer

    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_db_pool"]).get_db_pool
    ] = override_pool
    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_kafka_producer"]).get_kafka_producer
    ] = override_producer

    return application, producer


@pytest.mark.asyncio
async def test_whatsapp_e2e_webhook_to_kafka(app):
    """WhatsApp webhook → published to Kafka → TwiML returned."""
    application, producer = app

    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/whatsapp",
            data={
                "From": "whatsapp:+1234567890",
                "To": "whatsapp:+14155238886",
                "Body": "How do I reset my password?",
                "MessageSid": "SM_e2e_test",
                "AccountSid": "AC_test",
                "ProfileName": "Test User",
                "NumMedia": "0",
            },
        )

    assert response.status_code == 200
    assert "<Response>" in response.text
    producer.send_and_wait.assert_called_once()

    # Verify message content
    call_args = producer.send_and_wait.call_args
    published = json.loads(call_args[0][1].decode("utf-8"))
    assert published["customer_identifier"] == "+1234567890"
    assert published["channel"] == "whatsapp"
    assert "reset my password" in published["content"]
