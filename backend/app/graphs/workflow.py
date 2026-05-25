from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
  
from app.graphs.state import AgentState
from app.db.session import SessionLocal

from app.services.guardrail_service import GuardrailService
from app.services.classification_service import ClassificationService
from app.services.retrieval_service import RetrievalService
from app.services.decision_service import DecisionService
from app.services.drafting_service import DraftingService
from app.services.ticket_service import TicketService


def guardrail_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates whether the incoming ticket content passes regex & LLM safety checks.
    """
    trace_id = state["trace_id"]
    ticket_id = state["ticket_id"]
    text_to_check = f"Subject: {state['subject']}\nBody: {state['body']}"
    
    with SessionLocal() as db:
        try:
            result = GuardrailService.check_safety(
                trace_id=trace_id,
                ticket_id=ticket_id,
                text=text_to_check,
                db=db
            )
            
            TicketService.update_ticket(
                db=db,
                ticket_id=ticket_id,
                status="processing" if result.is_safe else "escalated"
            )

            db.commit()
        
        except Exception:
            db.rollback()
            raise
    
    status = "processing" if result.is_safe else "escalated"
    
    return {
        "is_safe": result.is_safe,
        "safety_reason": result.reason,
        "status": status
    }

def route_after_guardrail(state: AgentState) -> str:
    if state.get('is_safe', True):
        return "classify"
    return END


def classification_node(state: AgentState) -> Dict[str, Any]:
    """
    Classifies safe tickets into categories and extracts sentiment & priority profiles.
    """
    if not state.get("is_safe", True):
        return {
            "category": "General",
            "priority": "low",
            "confidence": 0.0,
            "sentiment": "neutral",
            "classification_reason": "Skipped classification: Ticket escalated as unsafe."
        }

    trace_id = state["trace_id"]
    ticket_id = state["ticket_id"]
    subject = state["subject"]
    body = state["body"]

    with SessionLocal() as db:
        try:
            result = ClassificationService.classify(
                trace_id=trace_id,
                ticket_id=ticket_id,
                subject=subject,
                body=body,
                db=db
            )

            TicketService.update_ticket(
                db=db,
                ticket_id=ticket_id,
                category=result.category,
                priority=result.priority,
                confidence_score=result.confidence,
                sentiment=result.sentiment
            )

            db.commit()
        
        except Exception:
            db.rollback()
            raise

    return {
        "category": result.category,
        "priority": result.priority,
        "confidence": result.confidence,
        "sentiment": result.sentiment,
        "classification_reason": result.reasoning
    }

def route_after_decision(state: AgentState) -> str:
    if state.get("routing_decision") == "autodraft":
        return "draft"
    return END


def retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    Queries PGVector similarity index to extract relevant company policy guidelines.
    """
    if not state.get("is_safe", True):
        return {
            "retrieved_docs": [],
            "retrieval_success": False
        }

    trace_id = state["trace_id"]
    ticket_id = state["ticket_id"]
    subject = state["subject"]
    body = state["body"]
    search_query = f"{subject} {body}"

    with SessionLocal() as db:
        try:
            result = RetrievalService.retrieve_context(
                trace_id=trace_id,
                ticket_id=ticket_id,
                query=search_query,
                top_k=2,
                db=db
            )

            TicketService.update_ticket(
                db=db,
                ticket_id=ticket_id,
                retrieved_context=TicketService.serialize_retrieved_docs(
                    result.retrieved_docs
                )
            )
        
            db.commit()
        
        except Exception:
            db.rollback()
            raise

    return {
        "retrieved_docs": result.retrieved_docs,
        "retrieval_success": result.retrieval_success
    }


def decision_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes deterministic rules to route the ticket to 'autodraft' or 'escalate'.
    """
    # Reconstruct ClassificationResult from current state
    from app.schemas.classification import ClassificationResult
    classification = ClassificationResult(
        category=state.get("category", "General"),
        priority=state.get("priority", "medium"),
        confidence=state.get("confidence", 0.0),
        sentiment=state.get("sentiment", "neutral"),
        reasoning=state.get("classification_reason", "")
    )

    trace_id = state["trace_id"]
    ticket_id = state["ticket_id"]
    retrieval_success = state.get("retrieval_success", False)

    with SessionLocal() as db:
        try:
            result = DecisionService.route_ticket(
                trace_id=trace_id,
                ticket_id=ticket_id,
                classification=classification,
                retrieval_success=retrieval_success,
                db=db
            )

            TicketService.update_ticket(
                db=db,
                ticket_id=ticket_id,
                decision=result.decision,
                status="processing" if result.decision == "autodraft" else "escalated"
            )

            db.commit()
        
        except Exception:
            db.rollback()
            raise

    status = "processing" if result.decision == "autodraft" else "escalated"

    return {
        "routing_decision": result.decision,
        "routing_reason": result.reason,
        "status": status
    }


def drafting_node(state: AgentState) -> Dict[str, Any]:
    """
    Generates grounded support responses with strict guidelines citation.
    """
    if state.get("routing_decision") != "autodraft":
        return {
            "draft_response": None,
            "cited_sources": []
        }

    trace_id = state["trace_id"]
    ticket_id = state["ticket_id"]
    subject = state["subject"]
    body = state["body"]
    retrieved_docs = state["retrieved_docs"]

    with SessionLocal() as db:
        try:
            result = DraftingService.draft_response(
                trace_id=trace_id,
                ticket_id=ticket_id,
                subject=subject,
                body=body,
                retrieved_docs=retrieved_docs,
                db=db
            )

            TicketService.update_ticket(
                db=db,
                ticket_id=ticket_id,
                draft_response=result.response,
                status="completed"
            )

            db.commit()
        
        except Exception:
            db.rollback()
            raise

    return {
        "draft_response": result.response,
        "cited_sources": result.cited_sources
    }

checkpointer = None
workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("classify", classification_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("decide", decision_node)
workflow.add_node("draft", drafting_node)

# Flow execution graph transitions
workflow.add_edge(START, "guardrail")

workflow.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "classify": "classify",
        END: END
    }
)

workflow.add_edge("classify", "retrieve")
workflow.add_edge("retrieve", "decide")

workflow.add_conditional_edges(
    "decide",
    route_after_decision,
    {
        "draft": "draft",
        END: END
    }
)

workflow.add_edge("draft", END)

app_workflow = workflow.compile()

app_workflow