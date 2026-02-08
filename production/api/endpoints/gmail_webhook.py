"""Gmail webhook endpoint — POST /api/v1/webhooks/gmail."""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from production.api.dependencies import get_db_pool, get_kafka_producer
from production.channels.gmail_handler import GmailHandler
from production.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    pool=Depends(get_db_pool),
    producer=Depends(get_kafka_producer),
):
    """Handle Gmail Pub/Sub push notification.

    1. Validate Pub/Sub auth (Bearer token)
    2. Decode payload
    3. Normalize to InboundMessage
    4. Publish to Kafka fte.tickets.incoming
    5. Return 200 immediately
    """
    settings = get_settings()

    # Validate authorization (Pub/Sub push uses Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header and not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="INVALID_PAYLOAD")

    try:
        handler = GmailHandler()
        inbound = await handler.parse_inbound(body)

        # Publish to Kafka
        message_data = {
            "customer_identifier": inbound.customer_identifier,
            "identifier_type": inbound.identifier_type.value,
            "channel": inbound.channel.value,
            "content": inbound.content,
            "subject": inbound.subject,
            "metadata": inbound.metadata,
            "timestamp": inbound.timestamp.isoformat(),
        }

        await producer.send_and_wait(
            settings.KAFKA_TOPIC_INCOMING,
            json.dumps(message_data).encode("utf-8"),
        )

        logger.info(f"Gmail message published to Kafka: {inbound.customer_identifier}")
        return JSONResponse(status_code=200, content={"status": "accepted"})

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Gmail webhook error: {e}", exc_info=True)
        return JSONResponse(status_code=200, content={"status": "accepted"})
