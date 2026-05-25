import sys
import uuid
import json
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.db.models.ticket import Ticket
from app.db.models.trace import Trace
from app.graphs.workflow import app_workflow


def run_test_workflow(ticket_path: str):
    print(f"\n==================================================")
    print(f"Running E2E Test Workflow for: {Path(ticket_path).name}")
    print(f"==================================================")

    # 1. Load Synthetic Ticket File
    with open(ticket_path, "r") as f:
        ticket_data = json.load(f)

    # 2. Insert Base Ticket into PostgreSQL
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
        print(f"Created base ticket in PostgreSQL: ID={ticket_id}")

    # 3. Generate Trace ID and Prepare LangGraph Inputs
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

    # 4. Invoke LangGraph Orchestration DAG
    print("Invoking LangGraph DAG Conductor...")
    outputs = app_workflow.invoke(inputs)

    # 5. Fetch Final Ticket State & Traces from DB
    with SessionLocal() as db:
        final_ticket = db.get(Ticket, ticket_id)
        traces = db.query(Trace).filter(Trace.ticket_id == ticket_id).all()

    print("\n================== WORKFLOW OUTPUTS ==============")
    print(f"Final Graph State Status: {outputs.get('status')}")
    print(f"Is Safe:                  {outputs.get('is_safe')} ({outputs.get('safety_reason')})")
    print(f"Category:                 {outputs.get('category')} (Confidence: {outputs.get('confidence')})")
    print(f"Priority:                 {outputs.get('priority')}")
    print(f"Sentiment:                {outputs.get('sentiment')}")
    print(f"Routing Decision:         {outputs.get('routing_decision')} ({outputs.get('routing_reason')})")
    if outputs.get("draft_response"):
        print(f"Draft Response:\n---\n{outputs.get('draft_response')}\n---")
        print(f"Cited Sources:            {outputs.get('cited_sources')}")

    print("\n================== DATABASE SYNC CHECK ==============")
    print(f"Ticket Status in DB:      {final_ticket.status}")
    print(f"Ticket Decision in DB:    {final_ticket.decision}")
    print(f"Confidence Score in DB:   {final_ticket.confidence_score}")
    print(f"Logs Traces Recorded:     {len(traces)} execution steps")
    for t in traces:
        print(f"  - Node '{t.node_name}' ran in {int(t.latency_ms)}ms ({t.processing_status})")
    print(f"==================================================\n")


def generate_workflow_chart():
    print("\n==================================================")
    print("Generating Visual Workflow Chart...")
    print("==================================================")
    
    # 1. Print Mermaid Markdown (Dependency-free fallback)
    print("\n--- Visual Workflow Chart (Mermaid Markdown) ---")
    try:
        mermaid_markup = app_workflow.get_graph().draw_mermaid()
        print(mermaid_markup)
    except Exception as e:
        print(f"Failed to generate Mermaid: {e}")
    print("------------------------------------------------\n")

    # 2. Try saving to docs/workflow.png
    try:
        png_bytes = app_workflow.get_graph().draw_mermaid_png()
        docs_dir = Path(__file__).resolve().parent.parent / "docs"
        docs_dir.mkdir(exist_ok=True)
        img_path = docs_dir / "workflow.png"
        with open(img_path, "wb") as f:
            f.write(png_bytes)
        print(f"Successfully saved visual PNG flowchart to:\n   {img_path}")
    except Exception as e:
        print(f"Could not render PNG (requires graphviz/pygraphviz system library): {e}")
        print("Copy the Mermaid markup above and paste it into https://mermaid.live to view your chart!")
    print("==================================================\n")


if __name__ == "__main__":
    generate_workflow_chart()
    billing_json = Path(__file__).resolve().parent.parent / "synthetic_data" / "tickets" / "technical_issue_ticket.json"
    run_test_workflow(str(billing_json))