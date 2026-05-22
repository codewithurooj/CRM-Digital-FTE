"""WhatsApp webhook endpoint — supports Meta Cloud API and Twilio."""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, Response

from production.api.dependencies import get_db_pool, get_kafka_producer
from production.channels.whatsapp_handler import (
    WhatsAppHandler,
    validate_meta_signature,
    validate_twilio_signature,
)
from production.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhooks/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
):
    """Meta webhook verification handshake (GET).

    Meta sends this once when you register the webhook URL in the developer portal.
    Respond with hub.challenge if the verify token matches.
    """
    settings = get_settings()

    if hub_mode == "subscribe" and hub_verify_token == settings.META_WHATSAPP_VERIFY_TOKEN:
        logger.info("Meta WhatsApp webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)

    logger.warning(f"Meta webhook verification failed: mode={hub_mode}, token={hub_verify_token!r}")
    raise HTTPException(status_code=403, detail="VERIFICATION_FAILED")


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    pool=Depends(get_db_pool),
    producer=Depends(get_kafka_producer),
):
    """Handle inbound WhatsApp messages from Meta Cloud API or Twilio.

    Detects provider by Content-Type:
    - application/json  → Meta Cloud API
    - application/x-www-form-urlencoded → Twilio
    """
    settings = get_settings()
    content_type = request.headers.get("content-type", "")
    handler = WhatsAppHandler()

    # ── Meta Cloud API ────────────────────────────────────────────────────────
    if "application/json" in content_type:
        body_bytes = await request.body()

        # Validate X-Hub-Signature-256 if app secret is configured
        if settings.META_APP_SECRET:
            sig = request.headers.get("X-Hub-Signature-256", "")
            if not validate_meta_signature(body_bytes, sig, settings.META_APP_SECRET):
                raise HTTPException(status_code=403, detail="INVALID_SIGNATURE")

        payload = json.loads(body_bytes)

        # Meta sends status updates in the same webhook — ignore them
        if payload.get("object") != "whatsapp_business_account":
            return {"status": "ignored"}

        inbound = await handler.parse_inbound_meta(payload)
        if inbound is None:
            # Status update or unsupported message type — acknowledge silently
            return {"status": "ignored"}

        await _publish_to_kafka(producer, settings, inbound)
        logger.info(f"Meta WhatsApp message published: {inbound.customer_identifier}")
        return {"status": "ok"}

    # ── Twilio ────────────────────────────────────────────────────────────────
    form_data = await request.form()
    params = dict(form_data)

    if settings.TWILIO_AUTH_TOKEN:
        signature = request.headers.get("X-Twilio-Signature", "")
        if not validate_twilio_signature(str(request.url), params, signature, settings.TWILIO_AUTH_TOKEN):
            raise HTTPException(status_code=403, detail="INVALID_SIGNATURE")

    try:
        inbound = await handler.parse_inbound(params)
        await _publish_to_kafka(producer, settings, inbound)
        logger.info(f"Twilio WhatsApp message published: {inbound.customer_identifier}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)

    # Twilio expects TwiML acknowledgement
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


async def _publish_to_kafka(producer, settings, inbound) -> None:
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
