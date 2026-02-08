"""Contract tests for GET /api/v1/metrics/channels — response schema."""
import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app():
    pool, conn = make_mock_pool()
    conn.fetch = AsyncMock(return_value=[])

    from production.api.main import create_app

    application = create_app()

    async def override_pool():
        return pool

    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_db_pool"]).get_db_pool
    ] = override_pool

    return application


@pytest.mark.asyncio
async def test_metrics_returns_200(app):
    """Metrics endpoint returns 200 with period, channels, totals."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/metrics/channels")

    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "channels" in data
    assert "totals" in data


@pytest.mark.asyncio
async def test_metrics_period_has_fields(app):
    """Period includes start, end, duration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/metrics/channels")

    period = response.json()["period"]
    assert "start" in period
    assert "end" in period
    assert "duration" in period


@pytest.mark.asyncio
async def test_metrics_totals_has_fields(app):
    """Totals includes expected aggregate fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/metrics/channels")

    totals = response.json()["totals"]
    assert "total_conversations" in totals
    assert "total_escalations" in totals
    assert "total_messages" in totals
