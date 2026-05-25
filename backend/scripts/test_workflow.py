import sys
import uuid
import json
from pathlib import Path

# Setup system path to resolve app imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.db.models.ticket import Ticket
from app.db.models.trace import Trace
from app.graphs.workflow import app_workflow


def run_test_workflow(ticket_path: str):
    print(f"\n--- Testing workflow with: {Path(ticket_path).name} ---")

    # Load mock ticket data
    with open(ticket_path, "r") as f:
        ticket_data = json.load(f)

    # Insert initial ticket into DB to simulate incoming hook
    with SessionLocal() as db:
        ticket = Ticket(
            subject=ticket_data["subject"],
            body=ticket_data["body"],
            sender_email=ticket_data["sender_email"],
            status="open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id
        print(f"Created ticket in DB: ID={ticket_id}")

    trace_id = str(uuid.uuid4())
    inputs = {
        "ticket_id": ticket_id,
        "trace_id": trace_id,
        "subject": ticket.subject,
        "body": ticket.body,
        "sender_email": ticket.sender_email,
        "is_safe": None,
        "safety_reason": None,
        "category": None,
        "priority": None,
        "confidence": None,
        "sentiment": None,
        "classification_reason": None,
        "retrieved_docs": [],
        "retrieval_success": False,
        "routing_decision": None, 
        "routing_reason": None,
        "draft_response": None,
        "cited_sources": [],
        "status": "pending"
    }

    print("Running workflow graph...")
    outputs = app_workflow.invoke(inputs)

    # Verify database updates and trace records
    with SessionLocal() as db:
        final_ticket = db.get(Ticket, ticket_id)
        traces = db.query(Trace).filter(Trace.ticket_id == ticket_id).all()

    print("\n[WORKFLOW RESULT]")
    print(f"Status:            {outputs.get('status')}")
    print(f"Safety:            {outputs.get('is_safe')} ({outputs.get('safety_reason')})")
    print(f"Category:          {outputs.get('category')} (Confidence: {outputs.get('confidence')})")
    print(f"Priority:          {outputs.get('priority')}")
    print(f"Sentiment:         {outputs.get('sentiment')}")
    print(f"Routing:           {outputs.get('routing_decision')} ({outputs.get('routing_reason')})")
    if outputs.get("draft_response"):
        print(f"Response Draft:\n---\n{outputs.get('draft_response')}\n---")
        print(f"Cited Chunks:      {outputs.get('cited_sources')}")

    print("\n[DATABASE VERIFICATION]")
    print(f"Ticket Status:     {final_ticket.status}")
    print(f"Routing Decision:  {final_ticket.decision}")
    print(f"Confidence Score:  {final_ticket.confidence_score}")
    print(f"Recorded Traces:   {len(traces)} steps")
    for t in traces:
        print(f"  * Node '{t.node_name}' completed in {int(t.latency_ms)}ms ({t.processing_status})")
    print("--------------------------------------------------\n")


def generate_workflow_chart():
    print("Generating workflow architecture diagrams...")
    
    # Export Mermaid schema
    try:
        mermaid_markup = app_workflow.get_graph().draw_mermaid()
        print("\n--- Mermaid Schema ---")
        print(mermaid_markup)
        print("----------------------\n")
    except Exception as e:
        print(f"Mermaid generation failed: {e}")

    # Export PNG diagram if libraries exist
    try:
        png_bytes = app_workflow.get_graph().draw_mermaid_png()
        docs_dir = Path(__file__).resolve().parent.parent / "docs"
        docs_dir.mkdir(exist_ok=True)
        img_path = docs_dir / "workflow.png"
        with open(img_path, "wb") as f:
            f.write(png_bytes)
        print(f"Saved flowchart to: {img_path}")
    except Exception as e:
        print(f"Skipping PNG rendering (requires optional system Graphviz): {e}")


if __name__ == "__main__":
    from sqlalchemy import text
    from app.db.base import Base
    from app.db.session import engine
    from app.db import models

    # Run migrations/setup on fresh test runs
    print("Preparing test database...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    generate_workflow_chart()
    
    ticket_file = Path(__file__).resolve().parent.parent / "synthetic_data" / "tickets" / "ambiguous_ticket.json"
    run_test_workflow(str(ticket_file))
