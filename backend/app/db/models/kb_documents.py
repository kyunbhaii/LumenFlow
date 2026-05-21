import datetime

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class KBDocument(Base):

    __tablename__ = "kb_documents"

    # NOTE:
    # Embedding vector storage will be added in the next retrieval phase
    # after pgvector integration is configured.
    #
    # Retrieval is being implemented vertically:
    # ORM foundation -> embeddings -> vector storage ->
    # similarity search -> retrieval service.

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    source: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow
    )