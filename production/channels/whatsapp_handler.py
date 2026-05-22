"""WhatsApp channel handler — Meta Cloud API (primary) + Twilio (fallback)."""
import hashlib
import hmac
import logging
from datetime import datetime, timezone

from production.channels.base import ChannelHandler
from production.schemas.messages import InboundMessage, ChannelType, IdentifierType

logger = logging.getLogger(__name__)


class WhatsAppHandler(ChannelHandler):
    """Handler for WhatsApp messages via Meta Cloud API or Twilio webhook."""

    async def parse_inbound(self, raw_data: dict) -> InboundMessage:
        """Parse Twilio form-encoded webhook into a normalized InboundMessage."""
        from_number = raw_data.get("From", "")
        phone = from_number.replace("whatsapp:", "").strip()

        body = raw_data.get("Body", "").strip()
        if not body:
            body = "[Media message - text only supported]"

        return InboundMessage(
            customer_identifier=phone,
            identifier_type=IdentifierType.PHONE,
            channel=ChannelType.WHATSAPP,
            content=body,
            subject=None,
            metadata={
                "message_sid": raw_data.get("MessageSid", ""),
                "account_sid": raw_data.get("AccountSid", ""),
                "profile_name": raw_data.get("ProfileName", ""),
                "num_media": raw_data.get("NumMedia", "0"),
                "from_raw": from_number,
                "provider": "twilio",
            },
            timestamp=datetime.now(timezone.utc),
        )

    async def parse_inbound_meta(self, payload: dict) -> InboundMessage | None:
        """Parse Meta WhatsApp Cloud API webhook JSON into a normalized InboundMessage.

        Meta payload structure:
        {
          "object": "whatsapp_business_account",
          "entry": [{"changes": [{"value": {"messages": [...], "contacts": [...]}}]}]
        }
        Returns None if the payload contains no text message (e.g. status updates).
        """
        try:
            entry = payload.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})

            messages = value.get("messages", [])
            if not messages:
                return None

            msg = messages[0]
            if msg.get("type") != "text":
                body = "[Media message - text only supported]"
            else:
                body = msg.get("text", {}).get("body", "").strip() or "[Empty message]"

            phone = msg.get("from", "")
            contacts = value.get("contacts", [{}])
            profile_name = contacts[0].get("profile", {}).get("name", "") if contacts else ""
            message_id = msg.get("id", "")
            phone_number_id = value.get("metadata", {}).get("phone_number_id", "")

            return InboundMessage(
                customer_identifier=phone,
                identifier_type=IdentifierType.PHONE,
                channel=ChannelType.WHATSAPP,
                content=body,
                subject=None,
                metadata={
                    "message_id": message_id,
                    "profile_name": profile_name,
                    "phone_number_id": phone_number_id,
                    "provider": "meta",
                },
                timestamp=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Failed to parse Meta webhook payload: {e}")
            return None

    async def format_response(self, response: str, metadata: dict) -> str:
        """Format response concisely for WhatsApp — conversational, max 1600 chars."""
        ticket_number = metadata.get("ticket_number", "")
        ticket_ref = f"\n\nTicket: {ticket_number}" if ticket_number else ""

        full_response = f"{response}{ticket_ref}"

        if len(full_response) <= 1600:
            return full_response

        return _split_whatsapp_message(full_response)

    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool:
        """Send reply via Meta Cloud API (primary) or Twilio (fallback).

        Tries Meta first if META_WHATSAPP_PHONE_NUMBER_ID is configured.
        Falls back to Twilio if Meta credentials are absent.
        """
        from production.config import get_settings
        settings = get_settings()

        # Meta Cloud API (primary)
        if settings.META_WHATSAPP_PHONE_NUMBER_ID and settings.META_WHATSAPP_ACCESS_TOKEN:
            return await _deliver_via_meta(
                formatted, destination,
                phone_number_id=settings.META_WHATSAPP_PHONE_NUMBER_ID,
                access_token=settings.META_WHATSAPP_ACCESS_TOKEN,
            )

        # Twilio (fallback)
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return await _deliver_via_twilio(
                formatted, destination,
                account_sid=settings.TWILIO_ACCOUNT_SID,
                auth_token=settings.TWILIO_AUTH_TOKEN,
                from_number=settings.TWILIO_WHATSAPP_NUMBER,
            )

        logger.warning("No WhatsApp provider configured (Meta or Twilio), skipping delivery")
        return False


async def _deliver_via_meta(
    text: str, destination: str, phone_number_id: str, access_token: str
) -> bool:
    """Send message via Meta WhatsApp Cloud API."""
    try:
        import httpx

        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": destination.lstrip("+") if not destination.startswith("whatsapp:") else destination.replace("whatsapp:", ""),
            "type": "text",
            "text": {"body": text},
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            msg_id = data.get("messages", [{}])[0].get("id", "unknown")
            logger.info(f"Meta WhatsApp reply sent: id={msg_id}, to={destination}")
            return True

    except Exception as e:
        logger.error(f"Meta WhatsApp delivery failed: {e}")
        return False


async def _deliver_via_twilio(
    text: str, destination: str, account_sid: str, auth_token: str, from_number: str
) -> bool:
    """Send message via Twilio WhatsApp API."""
    try:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)
        to_number = destination if destination.startswith("whatsapp:") else f"whatsapp:{destination}"
        message = client.messages.create(body=text, from_=from_number, to=to_number)
        logger.info(f"Twilio WhatsApp reply sent: sid={message.sid}, to={destination}")
        return True

    except Exception as e:
        logger.error(f"Twilio WhatsApp delivery failed: {e}")
        return False


def validate_meta_signature(body: bytes, signature: str, app_secret: str) -> bool:
    """Validate X-Hub-Signature-256 header from Meta webhook."""
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def validate_twilio_signature(url: str, params: dict, signature: str, auth_token: str) -> bool:
    """Validate X-Twilio-Signature header."""
    sorted_params = sorted(params.items())
    data_string = url + "".join(f"{k}{v}" for k, v in sorted_params)

    import base64
    computed = hmac.new(
        auth_token.encode("utf-8"),
        data_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    expected = base64.b64encode(computed).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def _split_whatsapp_message(text: str, max_chars: int = 1600) -> str:
    """Split long text at sentence boundaries for WhatsApp."""
    if len(text) <= max_chars:
        return text

    sentences = []
    current = ""
    for char in text:
        current += char
        if char in ".!?" and current.strip():
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    messages = []
    current_msg = ""

    for sentence in sentences:
        if len(current_msg) + len(sentence) + 1 <= max_chars:
            current_msg = f"{current_msg} {sentence}".strip()
        else:
            if current_msg:
                messages.append(current_msg)
            current_msg = sentence[:max_chars]

    if current_msg:
        messages.append(current_msg)

    return "\n---\n".join(messages)
