"""Web form channel handler — parse form submissions, format semi-formal responses."""
from datetime import datetime, timezone

from production.channels.base import ChannelHandler
from production.schemas.messages import InboundMessage, ChannelType, IdentifierType


class WebFormHandler(ChannelHandler):
    """Handler for web support form submissions."""

    async def parse_inbound(self, raw_data: dict) -> InboundMessage:
        """Parse web form data into a normalized InboundMessage."""
        return InboundMessage(
            customer_identifier=raw_data["email"],
            identifier_type=IdentifierType.EMAIL,
            channel=ChannelType.WEB_FORM,
            content=raw_data["message"],
            subject=raw_data.get("subject"),
            metadata={
                "name": raw_data.get("name", ""),
                "category": raw_data.get("category", ""),
                "priority": raw_data.get("priority", "medium"),
            },
            timestamp=datetime.now(timezone.utc),
        )

    async def format_response(self, response: str, metadata: dict) -> str:
        """Format response semi-formally with ticket reference."""
        customer_name = metadata.get("customer_name", "there")
        ticket_number = metadata.get("ticket_number", "")

        formatted = f"Hi {customer_name},\n\n{response}"
        if ticket_number:
            formatted += f"\n\nYour ticket reference: {ticket_number}\nTrack your ticket at support.techcorp.io"
        return formatted

    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool:
        """Web form responses are stored in DB (API-retrievable). No push delivery."""
        # Web form responses are retrieved via GET /api/v1/tickets/{ticket_id}
        return True
