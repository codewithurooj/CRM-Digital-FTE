# API Contract: Ticket Status

## Endpoint

- **Method**: `GET`
- **Path**: `/api/v1/tickets/{ticket_id}`
- **Auth**: None (ticket ID serves as access token)

## Request

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string | Ticket number (e.g., `TKT-0001`) |

## Response

### Success (200 OK)

```json
{
  "ticket_id": "TKT-0006",
  "status": "resolved",
  "category": "how_to",
  "priority": "low",
  "subject": "How to set up automations?",
  "source_channel": "web_form",
  "created_at": "2026-02-08T14:30:00Z",
  "updated_at": "2026-02-08T14:35:00Z",
  "resolved_at": "2026-02-08T14:35:00Z",
  "responses": [
    {
      "content": "Hi Lisa, here is how to set up automations on the Starter plan...",
      "channel": "web_form",
      "created_at": "2026-02-08T14:35:00Z"
    }
  ]
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 404 | `TICKET_NOT_FOUND` | No ticket exists with the given ID |

### 404 Example

```json
{
  "error": "TICKET_NOT_FOUND",
  "message": "No ticket found with ID TKT-9999"
}
```

## Implementation Notes

- Ticket ID is the human-readable `TKT-XXXX` format
- Responses array includes all agent/system responses for this ticket
- Status values: `open`, `processing`, `waiting`, `resolved`, `escalated`, `closed`
