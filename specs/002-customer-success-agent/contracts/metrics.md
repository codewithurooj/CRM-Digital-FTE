# API Contract: Channel Metrics

## Endpoint

- **Method**: `GET`
- **Path**: `/api/v1/metrics/channels`
- **Auth**: None (internal use)

## Request

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | string | No | `24h` | Time window: `1h`, `6h`, `12h`, `24h`, `7d` |
| `channel` | string | No | all | Filter by channel: `email`, `whatsapp`, `web_form` |

## Response

### Success (200 OK)

```json
{
  "period": {
    "start": "2026-02-07T12:00:00Z",
    "end": "2026-02-08T12:00:00Z",
    "duration": "24h"
  },
  "channels": [
    {
      "channel": "web_form",
      "total_conversations": 45,
      "avg_sentiment": 0.65,
      "escalation_count": 5,
      "escalation_rate": 0.11,
      "avg_response_latency_ms": 1200,
      "message_volume": {
        "inbound": 52,
        "outbound": 48
      }
    },
    {
      "channel": "email",
      "total_conversations": 28,
      "avg_sentiment": 0.58,
      "escalation_count": 8,
      "escalation_rate": 0.29,
      "avg_response_latency_ms": 2100,
      "message_volume": {
        "inbound": 35,
        "outbound": 30
      }
    },
    {
      "channel": "whatsapp",
      "total_conversations": 33,
      "avg_sentiment": 0.72,
      "escalation_count": 3,
      "escalation_rate": 0.09,
      "avg_response_latency_ms": 900,
      "message_volume": {
        "inbound": 60,
        "outbound": 55
      }
    }
  ],
  "totals": {
    "total_conversations": 106,
    "avg_sentiment": 0.65,
    "total_escalations": 16,
    "overall_escalation_rate": 0.15
  }
}
```

## Implementation Notes

- Metrics are aggregated from the `agent_metrics` table
- Escalation rate alert threshold: > 25% triggers an alert event
- Response latency alert threshold: > 3000ms triggers an alert event
