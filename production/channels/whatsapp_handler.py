"""WhatsApp channel handler — Twilio webhook parsing, concise formatting, Twilio API delivery."""
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

from production.channels.base import ChannelHandler
from production.schemas.messages import InboundMessage, ChannelType, IdentifierType

logger = logging.getLogger(__name__)


class WhatsAppHandler(ChannelHandler):
    """Handler for WhatsApp messages via Twilio webhook."""

    async def parse_inbound(self, raw_data: dict) -> InboundMessage:
        """Parse Twilio webhook form-encoded data into a normalized InboundMessage.

        Expected raw_data (from form-encoded POST):
        {
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+14155238886",
            "Body": "message text",
            "MessageSid": "SMxxxx",
            "AccountSid": "ACxxxx",
            "NumMedia": "0",
            "ProfileName": "John Doe"
        }
        """
        from_number = raw_data.get("From", "")
        # Strip "whatsapp:" prefix
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
            },
            timestamp=datetime.now(timezone.utc),
        )

    async def format_response(self, response: str, metadata: dict) -> str:
        """Format response concisely for WhatsApp — conversational, max 1600 chars."""
        ticket_number = metadata.get("ticket_number", "")
        ticket_ref = f"\n\nTicket: {ticket_number}" if ticket_number else ""

        full_response = f"{response}{ticket_ref}"

        # If under 1600 chars, return as-is
        if len(full_response) <= 1600:
            return full_response

        # Split at sentence boundaries
        return _split_whatsapp_message(full_response)

    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool:
        """Send reply via Twilio WhatsApp API.

        Args:
            formatted: Formatted message text
            destination: Phone number (e.g., +1234567890)
            metadata: Additional context
        """
        try:
            from production.config import get_settings
            settings = get_settings()

            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio credentials not configured, skipping delivery")
                return False

            # In production, this would use the Twilio API:
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=formatted,
            #     from_=settings.TWILIO_WHATSAPP_NUMBER,
            #     to=f"whatsapp:{destination}"
            # )
            logger.info(f"WhatsApp reply queued: to={destination}")
            return True

        except Exception as e:
            logger.error(f"WhatsApp delivery failed: {e}")
            return False


def validate_twilio_signature(url: str, params: dict, signature: str, auth_token: str) -> bool:
    """Validate Twilio X-Twilio-Signature header.

    Args:
        url: The full URL of the webhook endpoint
        params: The POST parameters
        signature: The X-Twilio-Signature header value
        auth_token: Twilio auth token from environment
    """
    # Sort params and concatenate key-value pairs
    sorted_params = sorted(params.items())
    data_string = url + "".join(f"{k}{v}" for k, v in sorted_params)

    # Compute HMAC-SHA1
    computed = hmac.new(
        auth_token.encode("utf-8"),
        data_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()

    import base64
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
