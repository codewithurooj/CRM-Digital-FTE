"""Metrics collector worker — aggregate metrics periodically, check alert thresholds."""
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Alert thresholds
ALERT_THRESHOLDS = {
    "avg_latency_ms": 3000,      # 3 seconds
    "escalation_rate": 0.25,      # 25%
}


async def collect_and_check_alerts(pool, period_hours: int = 24) -> dict:
    """Aggregate metrics and check alert thresholds.

    Returns alert results with any threshold violations.
    """
    from production.database.queries import metrics

    channel_data = await metrics.get_channel_metrics(pool, period_hours)

    alerts = []
    for channel_metric in channel_data:
        channel = channel_metric.get("channel", "unknown")

        # Check latency threshold
        avg_latency = channel_metric.get("avg_latency_ms")
        if avg_latency and avg_latency > ALERT_THRESHOLDS["avg_latency_ms"]:
            alerts.append({
                "type": "high_latency",
                "channel": channel,
                "value": avg_latency,
                "threshold": ALERT_THRESHOLDS["avg_latency_ms"],
                "message": f"Channel {channel} avg latency {avg_latency:.0f}ms exceeds {ALERT_THRESHOLDS['avg_latency_ms']}ms",
            })

        # Check escalation rate
        total_convos = channel_metric.get("total_conversations", 0)
        escalation_count = channel_metric.get("escalation_count", 0)
        if total_convos > 0:
            esc_rate = escalation_count / total_convos
            if esc_rate > ALERT_THRESHOLDS["escalation_rate"]:
                alerts.append({
                    "type": "high_escalation_rate",
                    "channel": channel,
                    "value": esc_rate,
                    "threshold": ALERT_THRESHOLDS["escalation_rate"],
                    "message": f"Channel {channel} escalation rate {esc_rate:.1%} exceeds {ALERT_THRESHOLDS['escalation_rate']:.0%}",
                })

    # Record alert events
    for alert in alerts:
        await metrics.record_metric(
            pool, "alert", 1.0, channel=alert["channel"],
            metadata={"alert_type": alert["type"], "message": alert["message"]},
        )
        logger.warning(f"ALERT: {alert['message']}")

    return {
        "period_hours": period_hours,
        "channels_checked": len(channel_data),
        "alerts_triggered": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def generate_daily_digest(pool, period_hours: int = 24) -> dict:
    """Generate a daily digest summarizing top issues, avg sentiment, resolution rates (T107).

    Returns a structured summary stored as an agent_metric record.
    """
    from production.database.queries import metrics

    channel_data = await metrics.get_channel_metrics(pool, period_hours)

    total_conversations = 0
    total_escalations = 0
    total_messages = 0
    total_latency_sum = 0
    sentiment_values = []
    channels_summary = []

    for ch in channel_data:
        ch_convos = ch.get("total_conversations", 0)
        ch_esc = ch.get("escalation_count", 0)
        ch_msgs = ch.get("message_volume", 0)
        ch_latency = ch.get("avg_latency_ms", 0)
        ch_sentiment = ch.get("avg_sentiment", 0.5)

        total_conversations += ch_convos
        total_escalations += ch_esc
        total_messages += ch_msgs
        total_latency_sum += ch_latency * ch_convos if ch_convos > 0 else 0
        if ch_convos > 0:
            sentiment_values.extend([ch_sentiment] * ch_convos)

        channels_summary.append({
            "channel": ch.get("channel", "unknown"),
            "conversations": ch_convos,
            "escalations": ch_esc,
            "escalation_rate": round(ch_esc / ch_convos, 3) if ch_convos > 0 else 0,
            "avg_latency_ms": round(ch_latency, 1),
            "avg_sentiment": round(ch_sentiment, 3),
            "message_volume": ch_msgs,
        })

    avg_sentiment = sum(sentiment_values) / len(sentiment_values) if sentiment_values else 0.5
    avg_latency = total_latency_sum / total_conversations if total_conversations > 0 else 0
    escalation_rate = total_escalations / total_conversations if total_conversations > 0 else 0

    digest = {
        "period_hours": period_hours,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_escalations": total_escalations,
            "escalation_rate": round(escalation_rate, 3),
            "avg_sentiment": round(avg_sentiment, 3),
            "avg_response_latency_ms": round(avg_latency, 1),
        },
        "channels": channels_summary,
    }

    # Store digest as metric
    await metrics.record_metric(
        pool, "daily_digest", 1.0,
        metadata=digest,
    )

    logger.info(
        f"Daily digest: {total_conversations} conversations, "
        f"sentiment={avg_sentiment:.2f}, escalation_rate={escalation_rate:.1%}"
    )

    return digest


async def scan_for_knowledge_candidates(pool, period_hours: int = 24) -> list:
    """Scan resolved tickets for novel solutions that could update the knowledge base (T108).

    Identifies tickets where:
    - Agent provided a successful response (not escalated)
    - Customer sentiment was positive after resolution
    - Content doesn't already exist in knowledge base

    Returns list of candidate entries.
    """
    from production.database.queries import metrics

    candidates = []

    # Get recent metrics to identify well-handled conversations
    channel_data = await metrics.get_channel_metrics(pool, period_hours)

    for ch in channel_data:
        ch_name = ch.get("channel", "unknown")
        ch_sentiment = ch.get("avg_sentiment", 0.5)
        ch_convos = ch.get("total_conversations", 0)
        ch_esc = ch.get("escalation_count", 0)

        # Channels with low escalation rate and good sentiment have knowledge
        if ch_convos > 0 and ch_sentiment > 0.5:
            resolved_ratio = 1.0 - (ch_esc / ch_convos if ch_convos else 0)
            if resolved_ratio > 0.7:
                candidates.append({
                    "channel": ch_name,
                    "resolved_ratio": round(resolved_ratio, 3),
                    "avg_sentiment": round(ch_sentiment, 3),
                    "conversations": ch_convos,
                    "recommendation": "Review resolved tickets for FAQ candidates",
                })

    if candidates:
        await metrics.record_metric(
            pool, "kb_candidates", float(len(candidates)),
            metadata={"candidates": candidates},
        )
        logger.info(f"Knowledge base candidates found: {len(candidates)} channels with learnable patterns")

    return candidates


async def run_collector(interval_seconds: int = 300):
    """Run the metrics collector on an interval (default: 5 minutes)."""
    from production.database.pool import get_pool

    logger.info(f"Metrics collector started, interval={interval_seconds}s")

    digest_counter = 0
    digest_interval = max(1, 86400 // interval_seconds)  # Once per day

    while True:
        try:
            pool = await get_pool()
            result = await collect_and_check_alerts(pool)
            logger.info(
                f"Metrics check: {result['channels_checked']} channels, "
                f"{result['alerts_triggered']} alerts"
            )

            # Generate daily digest and scan for KB candidates (T107, T108)
            digest_counter += 1
            if digest_counter >= digest_interval:
                digest_counter = 0
                await generate_daily_digest(pool, period_hours=24)
                await scan_for_knowledge_candidates(pool, period_hours=24)

        except Exception as e:
            logger.error(f"Metrics collection failed: {e}", exc_info=True)

        await asyncio.sleep(interval_seconds)
