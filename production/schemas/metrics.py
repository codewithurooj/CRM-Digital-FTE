"""Pydantic schemas for channel metrics — per contracts/metrics.md."""
from datetime import datetime

from pydantic import BaseModel


class MetricsPeriod(BaseModel):
    start: datetime
    end: datetime
    duration: str


class ChannelMetric(BaseModel):
    channel: str
    total_conversations: int = 0
    avg_sentiment: float | None = None
    escalation_count: int = 0
    escalation_rate: float = 0.0
    avg_response_latency_ms: float | None = None
    message_volume: int = 0


class MetricsTotals(BaseModel):
    total_conversations: int = 0
    avg_sentiment: float | None = None
    total_escalations: int = 0
    avg_response_latency_ms: float | None = None
    total_messages: int = 0


class ChannelMetricsResponse(BaseModel):
    period: MetricsPeriod
    channels: list[ChannelMetric] = []
    totals: MetricsTotals = MetricsTotals()
