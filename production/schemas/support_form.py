"""Pydantic schemas for web support form — per contracts/web-form.md."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TicketCategory(str, Enum):
    ACCOUNT_ACCESS = "account_access"
    BILLING = "billing"
    TECHNICAL = "technical"
    HOW_TO = "how_to"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SupportFormRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    subject: str = Field(..., min_length=5, max_length=500)
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    message: str = Field(..., min_length=10)


class SupportFormResponse(BaseModel):
    ticket_id: str
    status: str = "received"
    message: str = "Your support request has been received. Our team will respond within 30 minutes."
    created_at: datetime
