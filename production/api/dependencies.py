"""Shared FastAPI dependencies — DB pool, Kafka producer."""
from production.database.pool import get_pool


async def get_db_pool():
    """FastAPI dependency: return the asyncpg connection pool."""
    return await get_pool()


async def get_kafka_producer():
    """FastAPI dependency: return the Kafka producer (lazy init)."""
    from production.kafka_client import get_producer
    return await get_producer()
