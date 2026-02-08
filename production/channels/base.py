"""Abstract channel handler interface — adapter pattern."""
from abc import ABC, abstractmethod

from production.schemas.messages import InboundMessage


class ChannelHandler(ABC):
    """Base class for channel-specific handlers."""

    @abstractmethod
    async def parse_inbound(self, raw_data: dict) -> InboundMessage:
        """Parse raw channel data into a normalized InboundMessage."""
        ...

    @abstractmethod
    async def format_response(self, response: str, metadata: dict) -> str:
        """Format agent response for this channel."""
        ...

    @abstractmethod
    async def deliver(self, formatted: str, destination: str, metadata: dict) -> bool:
        """Deliver the formatted response via this channel."""
        ...
