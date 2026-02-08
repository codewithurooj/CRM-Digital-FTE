"""Unit tests for customer queries — T013 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestCustomerQueries:

    @pytest.mark.asyncio
    async def test_create_customer(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "uuid-1", "email": "a@b.com", "name": "A"})
        from production.database.queries.customers import create_customer
        result = await create_customer(pool, "a@b.com", "A")
        assert result["email"] == "a@b.com"
        conn.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customer_by_email(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "uuid-1", "email": "a@b.com"})
        from production.database.queries.customers import get_customer_by_email
        result = await get_customer_by_email(pool, "a@b.com")
        assert result["id"] == "uuid-1"

    @pytest.mark.asyncio
    async def test_get_customer_by_email_not_found(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value=None)
        from production.database.queries.customers import get_customer_by_email
        result = await get_customer_by_email(pool, "nobody@x.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_identity(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={"id": "uuid-1", "email": "a@b.com"})
        from production.database.queries.customers import resolve_identity
        result = await resolve_identity(pool, "a@b.com", "email")
        assert result["id"] == "uuid-1"
