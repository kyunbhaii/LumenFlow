import datetime
import uuid

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    trace_id: Mapped[str] = mapped_column(
        String,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"),
        nullable=False,
        index=True
    )

    node_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    input_payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    output_payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    prompt_version: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    processing_status: Mapped[str] = mapped_column(
        String,
        default="SUCCESS"
    )

    fallback_reason: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow
    )