from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.classification import ClassificationResult
from app.schemas.decision import DecisionResult
from app.observability.trace_logger import TraceLogger
from app.schemas.trace import TraceCreate


class DecisionService:
    @staticmethod
    def route_ticket(
        trace_id: str,
        ticket_id: int,
        classification: ClassificationResult,
        retrieval_success: bool,
        db: Optional[Session] = None
    ) -> DecisionResult:
        """
        Deterministic Python business boundary router enforcing strict SLA & fallback rules.
        Decides whether to route the ticket to 'autodraft' or 'escalate' (manual support).
        """
        start_time = TraceLogger.start_timer()
        decision = "autodraft"
        reason = "Classification confidence and vector search results satisfy draft criteria."
        fallback_triggered = False
        fallback_reason = None

        # Threshold Rule 1: Confidence Boundary
        if classification.confidence < 0.65:
            decision = "escalate"
            reason = f"Classification confidence score is too low ({classification.confidence} < 0.65)."
            fallback_triggered = True
            fallback_reason = "low_classification_confidence"

        # Threshold Rule 2: Ingestion/Vector Search Degradation Safeguard
        elif not retrieval_success:
            decision = "escalate"
            reason = "Retrieval pipeline failed, timed out, or returned degraded scores."
            fallback_triggered = True
            fallback_reason = "degraded_vector_search"

        latency_ms = TraceLogger.end_timer(start_time)

        # Log routing decisions in tracing layer
        event = TraceCreate(
            trace_id=trace_id,
            ticket_id=ticket_id,
            node_name="decision_service",
            input_payload={
                "confidence": classification.confidence,
                "retrieval_success": retrieval_success
            },
            output_payload={"decision": decision, "reason": reason},
            latency_ms=int(latency_ms),
            prompt_version="deterministic_v1",
            processing_status="SUCCESS",
            fallback_reason=fallback_reason if fallback_triggered else None,
            error_message=None
        )
        if db:
            TraceLogger.log_event(db, event)

        return DecisionResult(
            decision=decision,
            reason=reason,
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason
        )