"""Channel handlers — adapter pattern for multi-channel support."""
from production.channels.base import ChannelHandler
from production.channels.web_form_handler import WebFormHandler
from production.channels.gmail_handler import GmailHandler
from production.channels.whatsapp_handler import WhatsAppHandler

__all__ = ["ChannelHandler", "WebFormHandler", "GmailHandler", "WhatsAppHandler"]

CHANNEL_HANDLERS = {
    "web_form": WebFormHandler,
    "email": GmailHandler,
    "whatsapp": WhatsAppHandler,
}


def get_handler(channel: str) -> ChannelHandler:
    """Return the appropriate channel handler instance."""
    handler_class = CHANNEL_HANDLERS.get(channel)
    if not handler_class:
        raise ValueError(f"Unknown channel: {channel}")
    return handler_class()
