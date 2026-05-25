import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket
from app.schemas.retrieval import RetrievedDocument


class TicketService:
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Ticket:
        ticket = db.get(Ticket, ticket_id)
        if ticket is None:
            raise ValueError(f"Ticket with id={ticket_id} not found.")
        return ticket

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        **fields: Any
    ) -> Ticket:
        ticket = TicketService.get_ticket(db, ticket_id)

        for field_name, value in fields.items():
            if value is None:
                continue

            if not hasattr(ticket, field_name):
                raise ValueError(
                    f"Ticket has no field named '{field_name}'."
                )

            setattr(ticket, field_name, value)

        db.add(ticket)
        db.flush()
        return ticket

    @staticmethod
    def serialize_retrieved_docs(
        docs: list[RetrievedDocument]
    ) -> str:
        return json.dumps(
            [doc.model_dump() for doc in docs]
        )