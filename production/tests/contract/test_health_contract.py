"""Contract tests for GET /api/v1/health — response schema validation."""
import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport

from production.tests.conftest import make_mock_pool


@pytest.fixture
def app():
    pool, conn = make_mock_pool()
    conn.fetchval = AsyncMock(return_value=1)

    from production.api.main import create_app

    application = create_app()

    async def override_pool():
        return pool

    application.dependency_overrides[
        __import__("production.api.dependencies", fromlist=["get_db_pool"]).get_db_pool
    ] = override_pool

    return application


@pytest.mark.asyncio
async def test_health_returns_200(app):
    """Health endpoint returns 200 with status, components, version, timestamp."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_has_all_components(app):
    """Health response includes database, kafka, gmail, whatsapp, agent components."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    data = response.json()
    components = data["components"]
    assert "database" in components
    assert "kafka" in components
    assert "gmail" in components
    assert "whatsapp" in components
    assert "agent" in components


@pytest.mark.asyncio
async def test_health_component_has_status(app):
    """Each component has a status field."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    data = response.json()
    for name, comp in data["components"].items():
        assert "status" in comp, f"Component {name} missing status"
        assert comp["status"] in ("healthy", "degraded", "unhealthy")
