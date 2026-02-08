# API Contract: WhatsApp Webhook (Twilio)

## Endpoint

- **Method**: `POST`
- **Path**: `/api/v1/webhooks/whatsapp`
- **Auth**: Twilio request signature validation
- **SLA**: Response within 500ms

## Request

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | `application/x-www-form-urlencoded` |
| X-Twilio-Signature | Yes | HMAC signature for request validation |

### Body (Form-Encoded)

| Field | Type | Description |
|-------|------|-------------|
| `From` | string | Sender WhatsApp number (e.g., `whatsapp:+14155551001`) |
| `Body` | string | Message text content |
| `To` | string | TechCorp WhatsApp number |
| `MessageSid` | string | Twilio message SID |
| `AccountSid` | string | Twilio account SID |
| `NumMedia` | string | Number of media attachments (usually "0") |

## Response

### Success (200 OK)

Returns TwiML (empty response — actual reply sent async via Twilio API):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `MALFORMED_PAYLOAD` | Missing required Twilio fields |
| 403 | `INVALID_SIGNATURE` | X-Twilio-Signature validation failed |
| 500 | `INTERNAL_ERROR` | Server error during processing |

## Implementation Notes

- Twilio signature is validated using `twilio.request_validator.validate()` with the auth token
- Media attachments: If `NumMedia > 0`, the system acknowledges but informs the customer only text is supported
- "human" / "agent" / "representative" keywords trigger immediate escalation
- The handler normalizes the message and publishes to Kafka `fte.tickets.incoming`
- Replies are sent asynchronously via the Twilio REST API (not TwiML response)
