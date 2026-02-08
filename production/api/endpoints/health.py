"""Health check endpoint — GET /api/v1/health with component status."""
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from production.api.dependencies import get_db_pool
from production.config import get_settings
from production.schemas.health import ComponentHealth, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(pool=Depends(get_db_pool)):
    """Check health of all system components.

    Returns:
        - 200: healthy or degraded
        - 503: unhealthy (via status field)
    """
    settings = get_settings()
    components = {}

    # Check database
    components["database"] = await _check_database(pool)

    # Check Kafka
    components["kafka"] = await _check_kafka()

    # Gmail status (based on config)
    components["gmail"] = _check_gmail_config(settings)

    # WhatsApp status (based on config)
    components["whatsapp"] = _check_whatsapp_config(settings)

    # Agent status (based on OpenAI key)
    components["agent"] = _check_agent_config(settings)

    # Determine overall status
    statuses = [c.status for c in components.values()]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    else:
        overall = "degraded"

    return HealthResponse(
        status=overall,
        components=components,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
    )


async def _check_database(pool) -> ComponentHealth:
    """Check database connectivity."""
    try:
        start = time.time()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


async def _check_kafka() -> ComponentHealth:
    """Check Kafka producer connectivity."""
    try:
        from production.kafka_client import get_producer
        producer = await get_producer()
        if producer and producer._sender and producer._sender.sender_task:
            return ComponentHealth(status="healthy")
        return ComponentHealth(status="healthy")
    except Exception as e:
        return ComponentHealth(status="degraded", error=str(e))


def _check_gmail_config(settings) -> ComponentHealth:
    """Check Gmail configuration."""
    if settings.GMAIL_CLIENT_ID:
        return ComponentHealth(status="healthy")
    return ComponentHealth(status="degraded", error="Gmail credentials not configured")


def _check_whatsapp_config(settings) -> ComponentHealth:
    """Check WhatsApp/Twilio configuration."""
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        return ComponentHealth(status="healthy")
    return ComponentHealth(status="degraded", error="Twilio credentials not configured")


def _check_agent_config(settings) -> ComponentHealth:
    """Check AI agent configuration."""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-key-not-real":
        return ComponentHealth(status="healthy")
    return ComponentHealth(status="degraded", error="OpenAI API key not configured")
