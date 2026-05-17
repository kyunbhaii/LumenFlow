import datetime

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    # Primary Info
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    subject: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sender_email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    # ML Pipeline Outputs
    status: Mapped[str] = mapped_column(
        String,
        default="open",
        index=True
    )  # open, pending_review, closed, escalated

    priority: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )  # low, medium, high, urgent

    category: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    sentiment: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    # Decisions & Responses
    decision: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )  # autodraft, escalate, close

    draft_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    retrieved_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Human Feedback
    human_override: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )