"""Unit tests for metrics queries — T018 TDD target."""
import pytest
from unittest.mock import AsyncMock
from production.tests.conftest import make_mock_pool


class TestMetricsQueries:

    @pytest.mark.asyncio
    async def test_record_metric(self):
        pool, conn = make_mock_pool()
        conn.fetchrow = AsyncMock(return_value={
            "id": "m-1", "metric_type": "response_latency", "value": 1500.0
        })
        from production.database.queries.metrics import record_metric
        result = await record_metric(pool, "response_latency", 1500.0, channel="web_form")
        assert result["metric_type"] == "response_latency"

    @pytest.mark.asyncio
    async def test_get_channel_metrics(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[
            {"channel": "web_form", "total_conversations": 5, "avg_sentiment": 0.7}
        ])
        from production.database.queries.metrics import get_channel_metrics
        result = await get_channel_metrics(pool)
        assert result[0]["channel"] == "web_form"

    @pytest.mark.asyncio
    async def test_get_metrics_by_type(self):
        pool, conn = make_mock_pool()
        conn.fetch = AsyncMock(return_value=[{"metric_type": "escalation", "value": 1.0}])
        from production.database.queries.metrics import get_metrics_by_type
        result = await get_metrics_by_type(pool, "escalation")
        assert len(result) == 1
