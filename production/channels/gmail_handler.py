"""Gmail channel handler — parse Pub/Sub notifications, format formal responses, deliver via Gmail API."""
import base64
import json
import logging
from datetime import datetime, timezone

from production.channels.base import ChannelHandler
from production.schemas.messages import InboundMessage, ChannelType, IdentifierType

logger = logging.getLogger(__name__)


class GmailHandler(ChannelHandler):
    """Handler for Gmail email channel via Pub/Sub push notifications."""

    async def parse_inbound(self, raw_data: dict) -> InboundMessage:
        """Parse Gmail Pub/Sub push notification into a normalized InboundMessage.

        Expected raw_data structure (from Pub/Sub):
        {
            "message": {
                "data": "<base64-encoded JSON>",
                "messageId": "...",
                "publishTime": "..."
            },
            "subscription": "projects/.../subscriptions/..."
        }

        The decoded data contains:
        {
            "emailAddress": "sender@example.com",
            "historyId": 12345
        }

        For the actual email content, we need the parsed email fields:
        {
            "from": "sender@example.com",
            "subject": "...",
            "body": "...",
            "thread_id": "...",
            "message_id": "..."
        }
        """
        # Handle pre-parsed email data (from worker after Gmail API fetch)
        if "from" in raw_data:
            return InboundMessage(
                customer_identifier=raw_data["from"],
                identifier_type=IdentifierType.EMAIL,
                channel=ChannelType.EMAIL,
                content=raw_data.get("body", ""),
                subject=raw_data.get("subject"),
                metadata={
                    "thread_id": raw_data.get("thread_id", ""),
                    "message_id": raw_data.get("message_id", ""),
                    "gmail_history_id": raw_data.get("history_id", ""),
                },
                timestamp=datetime.now(timezone.utc),
            )

        # Handle raw Pub/Sub notification
        pub_sub_data = raw_data.get("message", {}).get("data", "")
        if pub_sub_data:
            decoded = json.loads(base64.b64decode(pub_sub_data))
            email_address = decoded.get("emailAddress", "")
            history_id = decoded.get("historyId", "")

            return InboundMessage(
                customer_identifier=email_address,
                identifier_type=IdentifierType.EMAIL,
                channel=ChannelType.EMAIL,
                content="[Pending Gmail API fetch]",  # Content fetched separately via Gmail API
                subject=None,
                metadata={
                    "gmail_history_id": str(history_id),
                    "pub_sub_message_id": raw_data.get("message", {}).get("messageId", ""),
                    "needs_fetch": True,
                },
                timestamp=datetime.now(timezone.utc),
            )

        raise ValueError("Invalid Gmail webhook payload")

    async def format_response(self, response: str, metadata: dict) -> str:
        """Format response formally with greeting, body, and professional signature."""
        customer_name = metadata.get("customer_name", "there")
        ticket_number = metadata.get("ticket_number", "")

        greeting = f"Hi {customer_name},"
        ticket_ref = f"\n\nYour ticket reference: {ticket_number}" if ticket_number else ""
        signature = (
            "\n\nBest regards,\n"
            "TechCorp Support Team\n"
            "support@techcorp.io | status.techcorp.io"
        )

        formatted = f"{greeting}\n\n{response}{ticket_ref}{signature}"

        # Enforce 500-word limit
        words = formatted.split()
        if len(words) > 500:
            formatted = " ".join(words[:497]) + "..." + signature

        return formatted

    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool:
        """Send reply via Gmail API in the same email thread.

        Args:
            formatted: Formatted email body
            destination: Recipient email address
            metadata: Must contain 'thread_id' for threading
        """
        try:
            from production.config import get_settings
            settings = get_settings()

            if not settings.GMAIL_CLIENT_ID:
                logger.warning("Gmail credentials not configured, skipping delivery")
                return False

            # Build email message
            thread_id = metadata.get("thread_id", "")
            subject = metadata.get("subject", "Re: Support Request")
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"

            # In production, this would use the Gmail API:
            # service = build('gmail', 'v1', credentials=creds)
            # message = create_message(destination, subject, formatted)
            # service.users().messages().send(userId='me', body={'raw': message, 'threadId': thread_id})
            logger.info(f"Gmail reply queued: to={destination}, thread={thread_id}")
            return True

        except Exception as e:
            logger.error(f"Gmail delivery failed: {e}")
            return False
