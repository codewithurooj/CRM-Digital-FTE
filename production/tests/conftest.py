"""Shared test fixtures for CRM Digital FTE."""
import os
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set test environment variables before any imports
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-not-real")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


def make_mock_pool(conn=None):
    """Create a mock asyncpg pool with proper async context manager for acquire().

    Usage:
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={...})
        result = await some_query(pool, ...)
    """
    if conn is None:
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        conn.fetch = AsyncMock(return_value=[])
        conn.execute = AsyncMock(return_value="INSERT 0 1")
        conn.fetchval = AsyncMock(return_value=None)

    pool = MagicMock()
    pool.close = AsyncMock()

    @asynccontextmanager
    async def mock_acquire():
        yield conn

    pool.acquire = mock_acquire
    return pool, conn


@pytest.fixture
def mock_db_pool():
    """Mock asyncpg connection pool with proper acquire() context manager."""
    pool, conn = make_mock_pool()
    return pool


@pytest.fixture
def mock_kafka_producer():
    """Mock aiokafka producer."""
    producer = AsyncMock()
    producer.start = AsyncMock()
    producer.stop = AsyncMock()
    producer.send_and_wait = AsyncMock()
    return producer


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI Agents SDK client."""
    client = MagicMock()
    return client


@pytest.fixture
def sample_form_data():
    """Valid web support form data."""
    return {
        "name": "Lisa Chen",
        "email": "lisa.chen@creativeagency.com",
        "subject": "How to set up automations?",
        "category": "how_to",
        "priority": "medium",
        "message": "I just upgraded to Starter and I am trying to set up an automation that sends a Slack notification. Can you walk me through it?",
    }


@pytest.fixture
def sample_inbound_message():
    """Sample normalized inbound message."""
    return {
        "customer_identifier": "lisa.chen@creativeagency.com",
        "identifier_type": "email",
        "channel": "web_form",
        "content": "How to set up automations?",
        "subject": "How to set up automations?",
        "metadata": {},
    }
