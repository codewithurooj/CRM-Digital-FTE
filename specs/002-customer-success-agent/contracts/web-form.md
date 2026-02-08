# API Contract: Web Support Form

## Endpoint

- **Method**: `POST`
- **Path**: `/api/v1/support/form`
- **Auth**: None (public endpoint)
- **SLA**: Response within 500ms

## Request

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | `application/json` |

### Body

```json
{
  "name": "string (min 2 chars, max 255)",
  "email": "string (valid email format)",
  "subject": "string (min 5 chars, max 500)",
  "category": "string (enum: account_access | billing | technical | how_to | feature_request | complaint)",
  "priority": "string (enum: low | medium | high) — default: medium",
  "message": "string (min 10 chars)"
}
```

### Validation Rules

- `name`: Required, minimum 2 characters, maximum 255 characters
- `email`: Required, must be a valid email format (contains `@` and domain)
- `subject`: Required, minimum 5 characters, maximum 500 characters
- `category`: Required, must be one of the allowed values
- `priority`: Optional, defaults to `medium`
- `message`: Required, minimum 10 characters

## Response

### Success (201 Created)

```json
{
  "ticket_id": "TKT-0001",
  "status": "received",
  "message": "Your support request has been received. Our team will respond within 30 minutes.",
  "created_at": "2026-02-08T12:00:00Z"
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | One or more fields failed validation |
| 500 | `INTERNAL_ERROR` | Server error during processing |
| 503 | `SERVICE_UNAVAILABLE` | Kafka or database unavailable |

### 400 Example

```json
{
  "error": "VALIDATION_ERROR",
  "details": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "message", "message": "Message must be at least 10 characters"}
  ]
}
```

## Examples

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/support/form \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lisa Chen",
    "email": "lisa.chen@creativeagency.com",
    "subject": "How to set up automations?",
    "category": "how_to",
    "priority": "low",
    "message": "I just upgraded to Starter and I am trying to set up an automation that sends a Slack notification. Can you walk me through it?"
  }'
```

### Example Response

```json
{
  "ticket_id": "TKT-0006",
  "status": "received",
  "message": "Your support request has been received. Our team will respond within 30 minutes.",
  "created_at": "2026-02-08T14:30:00Z"
}
```

## Implementation Notes

- The endpoint publishes a normalized message to Kafka `fte.tickets.incoming` and returns immediately
- Ticket creation happens synchronously (DB insert) before returning the ticket ID
- Agent processing happens asynchronously via Kafka consumer
