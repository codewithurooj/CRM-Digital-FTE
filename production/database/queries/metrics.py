"""Agent metrics recording and aggregation queries."""
import json


async def record_metric(pool, metric_type, value, channel=None, metadata=None):
    """Record a single metric data point."""
    meta_json = json.dumps(metadata or {})
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO agent_metrics (metric_type, value, channel, metadata)
               VALUES ($1, $2, $3, $4::jsonb)
               RETURNING *""",
            metric_type, value, channel, meta_json,
        )
        return dict(row) if row else None


async def get_channel_metrics(pool, period_hours=24):
    """Get aggregated metrics by channel for the given period."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT
                   channel,
                   COUNT(*) FILTER (WHERE metric_type = 'conversation_count') AS total_conversations,
                   AVG(value) FILTER (WHERE metric_type = 'sentiment') AS avg_sentiment,
                   COUNT(*) FILTER (WHERE metric_type = 'escalation') AS escalation_count,
                   AVG(value) FILTER (WHERE metric_type = 'response_latency') AS avg_latency_ms,
                   COUNT(*) FILTER (WHERE metric_type = 'message_volume') AS message_volume
               FROM agent_metrics
               WHERE recorded_at >= NOW() - ($1 || ' hours')::INTERVAL
                 AND channel IS NOT NULL
               GROUP BY channel""",
            str(period_hours),
        )
        return [dict(r) for r in rows]


async def get_metrics_by_type(pool, metric_type, limit=100):
    """Get recent metrics of a specific type."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM agent_metrics
               WHERE metric_type = $1
               ORDER BY recorded_at DESC
               LIMIT $2""",
            metric_type, limit,
        )
        return [dict(r) for r in rows]
