"""Unit tests for daily digest and knowledge base candidate scanning (Phase 14: T107-T108)."""
import pytest
from unittest.mock import AsyncMock, patch

from production.tests.conftest import make_mock_pool


@pytest.fixture
def mock_pool_with_metrics():
    pool, conn = make_mock_pool()
    conn.fetch = AsyncMock(return_value=[
        {
            "channel": "web_form",
            "total_conversations": 45,
            "avg_sentiment": 0.72,
            "escalation_count": 3,
            "avg_latency_ms": 1250.5,
            "message_volume": 90,
        },
        {
            "channel": "email",
            "total_conversations": 30,
            "avg_sentiment": 0.55,
            "escalation_count": 8,
            "avg_latency_ms": 2100.0,
            "message_volume": 60,
        },
    ])
    conn.fetchrow = AsyncMock(return_value={"id": "m-1"})
    conn.execute = AsyncMock()
    return pool


@pytest.mark.asyncio
async def test_generate_daily_digest(mock_pool_with_metrics):
    """Daily digest aggregates per-channel metrics."""
    from production.workers.metrics_collector import generate_daily_digest

    with patch("production.database.queries.metrics.get_channel_metrics", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {
                "channel": "web_form",
                "total_conversations": 45,
                "avg_sentiment": 0.72,
                "escalation_count": 3,
                "avg_latency_ms": 1250.5,
                "message_volume": 90,
            },
            {
                "channel": "email",
                "total_conversations": 30,
                "avg_sentiment": 0.55,
                "escalation_count": 8,
                "avg_latency_ms": 2100.0,
                "message_volume": 60,
            },
        ]
        with patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock):
            result = await generate_daily_digest(mock_pool_with_metrics, period_hours=24)

    assert result["period_hours"] == 24
    assert result["totals"]["total_conversations"] == 75
    assert result["totals"]["total_messages"] == 150
    assert result["totals"]["total_escalations"] == 11
    assert len(result["channels"]) == 2
    assert "generated_at" in result


@pytest.mark.asyncio
async def test_scan_for_knowledge_candidates(mock_pool_with_metrics):
    """Knowledge scan identifies channels with good resolution patterns."""
    from production.workers.metrics_collector import scan_for_knowledge_candidates

    with patch("production.database.queries.metrics.get_channel_metrics", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {
                "channel": "web_form",
                "total_conversations": 45,
                "avg_sentiment": 0.72,
                "escalation_count": 3,
                "message_volume": 90,
            },
        ]
        with patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock):
            candidates = await scan_for_knowledge_candidates(mock_pool_with_metrics, period_hours=24)

    assert len(candidates) >= 1
    assert candidates[0]["channel"] == "web_form"
    assert candidates[0]["resolved_ratio"] > 0.7


@pytest.mark.asyncio
async def test_scan_low_sentiment_no_candidates():
    """Channels with low sentiment should not be knowledge candidates."""
    from production.workers.metrics_collector import scan_for_knowledge_candidates
    pool, conn = make_mock_pool()

    with patch("production.database.queries.metrics.get_channel_metrics", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {
                "channel": "whatsapp",
                "total_conversations": 10,
                "avg_sentiment": 0.3,
                "escalation_count": 5,
                "message_volume": 20,
            },
        ]
        with patch("production.database.queries.metrics.record_metric", new_callable=AsyncMock):
            candidates = await scan_for_knowledge_candidates(pool, period_hours=24)

    assert len(candidates) == 0
