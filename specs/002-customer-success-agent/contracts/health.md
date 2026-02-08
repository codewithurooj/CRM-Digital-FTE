# API Contract: Health Check

## Endpoint

- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Auth**: None

## Request

No request body or parameters.

## Response

### Healthy (200 OK)

```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy", "latency_ms": 2},
    "kafka": {"status": "healthy", "latency_ms": 5},
    "gmail": {"status": "healthy"},
    "whatsapp": {"status": "healthy"},
    "agent": {"status": "healthy"}
  },
  "version": "0.1.0",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

### Degraded (200 OK)

```json
{
  "status": "degraded",
  "components": {
    "database": {"status": "healthy", "latency_ms": 2},
    "kafka": {"status": "healthy", "latency_ms": 5},
    "gmail": {"status": "unhealthy", "error": "OAuth token expired"},
    "whatsapp": {"status": "healthy"},
    "agent": {"status": "healthy"}
  },
  "version": "0.1.0",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

### Unhealthy (503 Service Unavailable)

```json
{
  "status": "unhealthy",
  "components": {
    "database": {"status": "unhealthy", "error": "Connection refused"},
    "kafka": {"status": "unhealthy", "error": "Broker unavailable"},
    "gmail": {"status": "unknown"},
    "whatsapp": {"status": "unknown"},
    "agent": {"status": "unknown"}
  },
  "version": "0.1.0",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

## Status Logic

- **healthy**: All critical components (database, kafka) are healthy
- **degraded**: Critical components healthy, but one or more non-critical components (gmail, whatsapp) are unhealthy
- **unhealthy**: Any critical component (database or kafka) is unhealthy — returns 503

## Implementation Notes

- Used as Kubernetes liveness and readiness probe target
- Database health: Execute `SELECT 1` and measure latency
- Kafka health: Check producer connection status
- Gmail/WhatsApp: Check OAuth token validity (cached, not checked every request)
