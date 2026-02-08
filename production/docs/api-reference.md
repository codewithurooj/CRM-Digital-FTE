# API Reference — CRM Digital FTE

Base URL: `http://localhost:8000/api/v1`

## POST /support/form

Submit a web support form.

**Request Body:**
```json
{
  "name": "Lisa Chen",
  "email": "lisa@example.com",
  "subject": "How to set up automations?",
  "category": "how_to",
  "priority": "medium",
  "message": "I need help setting up automation workflows."
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| name | string | Yes | min 2, max 255 chars |
| email | string | Yes | Valid email format |
| subject | string | Yes | min 5, max 500 chars |
| category | enum | Yes | account_access, billing, technical, how_to, feature_request, complaint |
| priority | enum | No | low, medium (default), high |
| message | string | Yes | min 10 chars |

**Response (201):**
```json
{
  "ticket_id": "TKT-0001",
  "status": "received",
  "message": "Your support request has been received. Our team will respond within 30 minutes.",
  "created_at": "2026-02-08T12:00:00Z"
}
```

**Errors:** 400 (invalid data), 422 (validation error), 503 (service unavailable)

---

## GET /tickets/{ticket_id}

Get ticket status by ticket number.

**Path Parameters:**
- `ticket_id`: Ticket number (e.g., TKT-0001)

**Response (200):**
```json
{
  "ticket_id": "TKT-0001",
  "status": "open",
  "category": "how_to",
  "priority": "medium",
  "subject": "How to set up automations?",
  "source_channel": "web_form",
  "created_at": "2026-02-08T12:00:00Z",
  "updated_at": "2026-02-08T12:00:00Z",
  "resolved_at": null,
  "responses": [
    {
      "content": "Hi Lisa, here's how to set up automations...",
      "channel": "web_form",
      "created_at": "2026-02-08T12:01:00Z"
    }
  ]
}
```

**Errors:** 404 (ticket not found)

---

## GET /health

System health check with component status.

**Response (200):**
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy", "latency_ms": 2.5},
    "kafka": {"status": "healthy"},
    "gmail": {"status": "degraded", "error": "Gmail credentials not configured"},
    "whatsapp": {"status": "degraded", "error": "Twilio credentials not configured"},
    "agent": {"status": "healthy"}
  },
  "version": "0.1.0",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

Status values: `healthy`, `degraded`, `unhealthy`

---

## GET /metrics/channels

Per-channel metrics for a configurable period.

**Query Parameters:**
- `period_hours`: 1-720 (default: 24)

**Response (200):**
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
      "avg_sentiment": 0.72,
      "escalation_count": 3,
      "escalation_rate": 0.067,
      "avg_response_latency_ms": 1250.5,
      "message_volume": 90
    }
  ],
  "totals": {
    "total_conversations": 100,
    "avg_sentiment": 0.68,
    "total_escalations": 8,
    "avg_response_latency_ms": 1500.0,
    "total_messages": 200
  }
}
```

---

## POST /webhooks/gmail

Gmail Pub/Sub push notification handler.

**Request Body (from Google Pub/Sub):**
```json
{
  "message": {
    "data": "<base64-encoded JSON>",
    "messageId": "pub-msg-123"
  },
  "subscription": "projects/techcorp/subscriptions/gmail-push"
}
```

**Response:** 200 `{"status": "accepted"}`

---

## POST /webhooks/whatsapp

Twilio WhatsApp webhook handler.

**Request Body (form-encoded):**
```
From=whatsapp:+1234567890&Body=Hello&MessageSid=SM123&AccountSid=AC456
```

**Headers Required:**
- `X-Twilio-Signature`: HMAC-SHA1 signature

**Response:** 200 (TwiML `<Response/>`)

**Errors:** 403 (invalid signature)
