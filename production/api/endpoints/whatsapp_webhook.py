"""WhatsApp webhook endpoint — POST /api/v1/webhooks/whatsapp."""
import json
import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response

from production.api.dependencies import get_db_pool, get_kafka_producer
from production.channels.whatsapp_handler import WhatsAppHandler, validate_twilio_signature
from production.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    pool=Depends(get_db_pool),
    producer=Depends(get_kafka_producer),
):
    """Handle Twilio WhatsApp webhook.

    1. Validate Twilio X-Twilio-Signature
    2. Parse form-encoded body
    3. Normalize to InboundMessage
    4. Publish to Kafka fte.tickets.incoming
    5. Return TwiML <Response/>
    """
    settings = get_settings()

    # Parse form-encoded body
    form_data = await request.form()
    params = dict(form_data)

    # Validate Twilio signature
    signature = request.headers.get("X-Twilio-Signature", "")
    if settings.TWILIO_AUTH_TOKEN:
        url = str(request.url)
        if not validate_twilio_signature(url, params, signature, settings.TWILIO_AUTH_TOKEN):
            raise HTTPException(status_code=403, detail="INVALID_SIGNATURE")

    try:
        handler = WhatsAppHandler()
        inbound = await handler.parse_inbound(params)

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

        logger.info(f"WhatsApp message published to Kafka: {inbound.customer_identifier}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)

    # Always return TwiML <Response/> to acknowledge
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )
