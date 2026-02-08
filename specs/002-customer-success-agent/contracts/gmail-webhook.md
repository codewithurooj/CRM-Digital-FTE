# API Contract: Gmail Webhook (Pub/Sub Push)

## Endpoint

- **Method**: `POST`
- **Path**: `/api/v1/webhooks/gmail`
- **Auth**: Google Pub/Sub push authentication (Bearer token)
- **SLA**: Response within 500ms

## Request

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | `application/json` |
| Authorization | Yes | `Bearer <token>` (Google Pub/Sub push token) |

### Body

```json
{
  "message": {
    "data": "string (base64-encoded notification data)",
    "messageId": "string (Pub/Sub message ID)",
    "publishTime": "string (ISO 8601 timestamp)"
  },
  "subscription": "string (Pub/Sub subscription name)"
}
```

### Decoded `message.data`

After base64 decoding, the data contains:

```json
{
  "emailAddress": "support@techcorp.com",
  "historyId": "12345"
}
```

The handler uses the `historyId` to fetch the actual email via Gmail API.

## Response

### Success (200 OK)

```json
{
  "status": "received"
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `MALFORMED_PAYLOAD` | Missing or invalid Pub/Sub message format |
| 401 | `UNAUTHORIZED` | Invalid or missing Bearer token |
| 500 | `INTERNAL_ERROR` | Server error during processing |

## Implementation Notes

- On receiving the push notification, the handler:
  1. Validates the Bearer token
  2. Decodes base64 `message.data`
  3. Calls Gmail API to fetch the email using `historyId`
  4. Extracts sender email, subject, and body
  5. Normalizes to `InboundMessage` format
  6. Publishes to Kafka `fte.tickets.incoming`
  7. Returns 200 immediately
- Gmail replies are sent via Gmail API in the same thread (using `threadId`)
