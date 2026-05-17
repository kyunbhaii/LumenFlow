from typing import Dict, Any
from app.observability.trace_logger import TraceLogger
from app.llm.structured_output import ClassificationOutput

class DecisionService:
    @staticmethod
    def route_ticket(trace_id: str, classification: ClassificationOutput, retrieval_success: bool) -> str:
        """
        Threshold-based routing logic. Returns 'autodraft', 'escalate', or 'close'.
        """
        start_time = TraceLogger.start_timer()
        
        decision = "autodraft"
        reason = "Confidence and retrieval are sufficient."
        
        # Threshold 1: Classification Confidence
        if classification.confidence < 0.65:
            decision = "escalate"
            reason = f"Classification confidence too low ({classification.confidence} < 0.65)"
            
        # Threshold 2: Retrieval Degradation
        elif not retrieval_success:
            decision = "escalate"
            reason = "Retrieval failed or degraded mode triggered, cannot safely autodraft."
            
        # Optional Threshold 3: Urgent priority
        # (Could add logic here based on sentiment or specific categories)
        
        TraceLogger.log_node_execution(
            trace_id=trace_id,
            node_name="decision_service",
            latency_ms=TraceLogger.end_timer(start_time),
            inputs={
                "confidence": classification.confidence,
                "retrieval_success": retrieval_success
            },
            outputs={"decision": decision, "reason": reason}
        )
        
        return decision
