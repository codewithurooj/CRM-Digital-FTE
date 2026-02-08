"""Unit tests for database connection pool — T011 TDD target."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestDatabasePool:
    """Test asyncpg connection pool lazy singleton."""

    def test_initial_pool_is_none(self):
        from production.database import pool as pool_module
        pool_module.reset_pool()
        assert pool_module._pool is None

    @pytest.mark.asyncio
    async def test_get_pool_creates_pool(self):
        from production.database import pool as pool_module
        pool_module.reset_pool()

        mock_pool = AsyncMock()
        with patch("production.database.pool.asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            result = await pool_module.get_pool(
                database_url="postgresql://test:test@localhost/test"
            )
            assert result is mock_pool
            mock_asyncpg.create_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pool_returns_same_instance(self):
        from production.database import pool as pool_module
        pool_module.reset_pool()

        mock_pool = AsyncMock()
        with patch("production.database.pool.asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            p1 = await pool_module.get_pool(database_url="postgresql://t:t@l/d")
            p2 = await pool_module.get_pool(database_url="postgresql://t:t@l/d")
            assert p1 is p2
            # create_pool should only be called once (singleton)
            assert mock_asyncpg.create_pool.call_count == 1

    @pytest.mark.asyncio
    async def test_close_pool(self):
        from production.database import pool as pool_module
        mock_pool = AsyncMock()
        pool_module._pool = mock_pool
        await pool_module.close_pool()
        mock_pool.close.assert_called_once()
        assert pool_module._pool is None

    @pytest.mark.asyncio
    async def test_check_health_returns_false_when_no_pool(self):
        from production.database import pool as pool_module
        pool_module.reset_pool()
        result = await pool_module.check_health()
        assert result is False

    @pytest.mark.asyncio
    async def test_check_health_returns_true_when_healthy(self):
        from production.database import pool as pool_module
        from production.tests.conftest import make_mock_pool

        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchval = AsyncMock(return_value=1)

        pool_module._pool = mock_pool
        result = await pool_module.check_health()
        assert result is True
        pool_module.reset_pool()
