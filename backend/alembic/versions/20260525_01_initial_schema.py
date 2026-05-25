"""initial schema

Revision ID: 20260525_01
Revises:
Create Date: 2026-05-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260525_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "kb_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_kb_documents_id"), "kb_documents", ["id"], unique=False)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("sender_email", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("sentiment", sa.String(), nullable=True),
        sa.Column("decision", sa.String(), nullable=True),
        sa.Column("draft_response", sa.Text(), nullable=True),
        sa.Column("retrieved_context", sa.Text(), nullable=True),
        sa.Column("human_override", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tickets_id"), "tickets", ["id"], unique=False)
    op.create_index(op.f("ix_tickets_sender_email"), "tickets", ["sender_email"], unique=False)
    op.create_index(op.f("ix_tickets_status"), "tickets", ["status"], unique=False)
    op.create_index(op.f("ix_tickets_subject"), "tickets", ["subject"], unique=False)

    op.create_table(
        "traces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("node_name", sa.String(), nullable=False),
        sa.Column("input_payload", sa.Text(), nullable=True),
        sa.Column("output_payload", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_version", sa.String(), nullable=True),
        sa.Column("processing_status", sa.String(), nullable=False),
        sa.Column("fallback_reason", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_traces_id"), "traces", ["id"], unique=False)
    op.create_index(op.f("ix_traces_ticket_id"), "traces", ["ticket_id"], unique=False)
    op.create_index(op.f("ix_traces_trace_id"), "traces", ["trace_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_traces_trace_id"), table_name="traces")
    op.drop_index(op.f("ix_traces_ticket_id"), table_name="traces")
    op.drop_index(op.f("ix_traces_id"), table_name="traces")
    op.drop_table("traces")

    op.drop_index(op.f("ix_tickets_subject"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_status"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_sender_email"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_id"), table_name="tickets")
    op.drop_table("tickets")

    op.drop_index(op.f("ix_kb_documents_id"), table_name="kb_documents")
    op.drop_table("kb_documents")

    op.execute("DROP EXTENSION IF EXISTS vector")
