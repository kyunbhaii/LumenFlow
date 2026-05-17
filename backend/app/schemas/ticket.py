from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class TicketBase(BaseModel):
    subject: str
    body: str
    sender_email: EmailStr


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    confidence_score: Optional[float] = None
    sentiment: Optional[str] = None
    decision: Optional[str] = None
    draft_response: Optional[str] = None
    retrieved_context: Optional[str] = None
    human_override: Optional[bool] = None


class TicketResponse(TicketBase):
    id: int

    status: str
    priority: Optional[str] = None
    category: Optional[str] = None
    confidence_score: Optional[float] = None
    sentiment: Optional[str] = None

    decision: Optional[str] = None
    draft_response: Optional[str] = None
    retrieved_context: Optional[str] = None

    human_override: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)