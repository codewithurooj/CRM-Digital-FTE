"""Asyncpg connection pool — lazy singleton pattern."""
import asyncpg

_pool: asyncpg.Pool | None = None


async def get_pool(database_url: str | None = None, min_size: int = 5, max_size: int = 20) -> asyncpg.Pool:
    """Return or create the asyncpg connection pool (lazy singleton)."""
    global _pool
    if _pool is None:
        if database_url is None:
            from production.config import get_settings
            settings = get_settings()
            database_url = settings.DATABASE_URL
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=min_size,
            max_size=max_size,
        )
    return _pool


async def close_pool() -> None:
    """Close the connection pool if it exists."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def check_health() -> bool:
    """Check if the database connection is healthy."""
    global _pool
    if _pool is None:
        return False
    try:
        async with _pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            return result == 1
    except Exception:
        return False


def reset_pool() -> None:
    """Reset pool reference (for testing)."""
    global _pool
    _pool = None
