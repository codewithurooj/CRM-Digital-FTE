"""Channel metrics endpoint — GET /api/v1/metrics/channels."""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query

from production.api.dependencies import get_db_pool
from production.database.queries import metrics as metric_queries
from production.schemas.metrics import (
    ChannelMetric,
    ChannelMetricsResponse,
    MetricsPeriod,
    MetricsTotals,
)

router = APIRouter()


@router.get("/metrics/channels", response_model=ChannelMetricsResponse)
async def get_channel_metrics(
    period_hours: int = Query(default=24, ge=1, le=720),
    pool=Depends(get_db_pool),
):
    """Get per-channel metrics for the given period.

    Returns conversation counts, sentiment averages, escalation counts/rates,
    response latency, and message volume per channel.
    """
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=period_hours)

    raw_metrics = await metric_queries.get_channel_metrics(pool, period_hours)

    channels = []
    total_conversations = 0
    total_escalations = 0
    total_messages = 0
    all_sentiments = []
    all_latencies = []

    for row in raw_metrics:
        convos = row.get("total_conversations", 0) or 0
        esc_count = row.get("escalation_count", 0) or 0
        esc_rate = (esc_count / convos) if convos > 0 else 0.0
        avg_sentiment = row.get("avg_sentiment")
        avg_latency = row.get("avg_latency_ms")
        msg_volume = row.get("message_volume", 0) or 0

        channels.append(ChannelMetric(
            channel=row.get("channel", "unknown"),
            total_conversations=convos,
            avg_sentiment=round(avg_sentiment, 3) if avg_sentiment else None,
            escalation_count=esc_count,
            escalation_rate=round(esc_rate, 3),
            avg_response_latency_ms=round(avg_latency, 1) if avg_latency else None,
            message_volume=msg_volume,
        ))

        total_conversations += convos
        total_escalations += esc_count
        total_messages += msg_volume
        if avg_sentiment is not None:
            all_sentiments.append(avg_sentiment)
        if avg_latency is not None:
            all_latencies.append(avg_latency)

    totals = MetricsTotals(
        total_conversations=total_conversations,
        avg_sentiment=round(sum(all_sentiments) / len(all_sentiments), 3) if all_sentiments else None,
        total_escalations=total_escalations,
        avg_response_latency_ms=round(sum(all_latencies) / len(all_latencies), 1) if all_latencies else None,
        total_messages=total_messages,
    )

    return ChannelMetricsResponse(
        period=MetricsPeriod(
            start=start,
            end=now,
            duration=f"{period_hours}h",
        ),
        channels=channels,
        totals=totals,
    )
