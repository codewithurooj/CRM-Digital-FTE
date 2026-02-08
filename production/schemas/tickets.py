"""Pydantic schemas for ticket responses — per contracts/tickets.md."""
from datetime import datetime

from pydantic import BaseModel


class TicketResponseEntry(BaseModel):
    content: str
    channel: str
    created_at: datetime


class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    category: str
    priority: str
    subject: str
    source_channel: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    responses: list[TicketResponseEntry] = []
