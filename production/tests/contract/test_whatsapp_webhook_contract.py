"""Contract tests for POST /api/v1/webhooks/whatsapp — form-encoded, TwiML, signature."""
import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def mock_deps():
    pool, conn = make_mock_pool()
    producer = AsyncMock()
    producer.send_and_wait = AsyncMock()
    return pool, producer


@pytest.fixture
def app(mock_deps):
    pool, producer = mock_deps
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

    return application


@pytest.mark.asyncio
async def test_whatsapp_webhook_returns_twiml(app):
    """Valid webhook returns TwiML <Response/>."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/whatsapp",
            data={
                "From": "whatsapp:+1234567890",
                "Body": "Hello",
                "MessageSid": "SM123",
                "AccountSid": "AC456",
            },
        )

    assert response.status_code == 200
    assert "<Response>" in response.text
    assert "application/xml" in response.headers.get("content-type", "")
