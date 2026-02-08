"""Worker modules — Kafka consumers for async message processing."""
from production.workers.message_processor import (
    process_kafka_message, run_worker, score_sentiment, route_priority_by_sentiment,
)
from production.workers.metrics_collector import (
    collect_and_check_alerts, run_collector, generate_daily_digest, scan_for_knowledge_candidates,
)

__all__ = [
    "process_kafka_message", "run_worker", "score_sentiment", "route_priority_by_sentiment",
    "collect_and_check_alerts", "run_collector", "generate_daily_digest", "scan_for_knowledge_candidates",
]
