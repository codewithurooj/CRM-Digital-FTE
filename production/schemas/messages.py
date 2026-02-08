"""Pydantic schemas for messages — unified inbound/outbound format."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class IdentifierType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"


class InboundMessage(BaseModel):
    customer_identifier: str
    identifier_type: IdentifierType
    channel: ChannelType
    content: str = Field(..., min_length=1)
    subject: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OutboundMessage(BaseModel):
    customer_id: str
    channel: ChannelType
    content: str
    ticket_number: str | None = None
    conversation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
