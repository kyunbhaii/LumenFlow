from typing import TypedDict, List, Optional
from app.schemas.retrieval import RetrievedDocument

class AgentState(TypedDict):
    # Ticket Identity & Content
    ticket_id: int
    trace_id: str
    subject: str
    body: str
    sender_email: str

    # Security Guardrails
    is_safe: Optional[bool]
    safety_reason: Optional[str]

    # Classification Triage
    category: Optional[str]
    priority: Optional[str]
    confidence: Optional[float]
    sentiment: Optional[str]
    classification_reason: Optional[str]

    # Retrieval Context
    retrieved_docs: List[RetrievedDocument]
    retrieval_success: bool

    # Routing Matrix 
    routing_decision: Optional[str]  # "autodraft" | "escalate"
    routing_reason: Optional[str]

    # Final Draft Response
    draft_response: Optional[str]
    cited_sources: List[str]

    # Overall State Status
    status: str  # "pending" | "processing" | "escalated" | "completed"