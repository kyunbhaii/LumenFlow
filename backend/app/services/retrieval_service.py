from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.retrieval.retriever import LumenRetriever
from app.schemas.retrieval import RetrievedDocument, RetrievalResult
from app.observability.trace_logger import TraceLogger
from app.schemas.trace import TraceCreate

# Initialize retriever lazily to avoid heavy Torch model loads during module imports
_retriever_instance: Optional[LumenRetriever] = None

def get_retriever() -> LumenRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = LumenRetriever(db_url=settings.SQLALCHEMY_DATABASE_URL)
    return _retriever_instance


class RetrievalService:
    @staticmethod
    def retrieve_context(
        trace_id: str,
        ticket_id: int,
        query: str,
        top_k: int = 3,
        db: Optional[Session] = None
    ) -> RetrievalResult:
        """
        Formulates a search query, performs similarity retrieval, and logs the telemetry.
        Gracefully handles database failures as a visible degraded mode.
        Returns a structured RetrievalResult object.
        """
        start_time = TraceLogger.start_timer()
        retrieved_docs: List[RetrievedDocument] = []
        retrieval_success = True
        error_msg = None
        fallback_reason = None

        try:
            retriever = get_retriever()
            retrieved_docs = retriever.retrieve(query=query, top_k=top_k)
            
            # Degraded Mode: Check if retrieved documents have very poor similarity scores
            # If our best match is below 0.35 similarity, we treat it as an ungrounded search
            if not retrieved_docs or all(doc.similarity_score < 0.35 for doc in retrieved_docs):
                retrieval_success = False
                fallback_reason = "low_similarity_score_degradation"
                
        except Exception as e:
            error_msg = str(e)
            retrieval_success = False
            fallback_reason = f"Vector DB operational failure: {error_msg}"
            retrieved_docs = []

        latency_ms = TraceLogger.end_timer(start_time)

        # Pack and write traces
        event = TraceCreate(
            trace_id=trace_id,
            ticket_id=ticket_id,
            node_name="retrieval_service",
            input_payload={"query": query, "top_k": top_k},
            output_payload=[doc.model_dump() for doc in retrieved_docs],
            latency_ms=int(latency_ms),
            prompt_version="vector_search_v1",
            processing_status="SUCCESS" if retrieval_success else "FAILED",
            fallback_reason=fallback_reason,
            error_message=error_msg
        )
        
        if db:
            TraceLogger.log_event(db, event)

        return RetrievalResult(
            retrieved_docs=retrieved_docs,
            retrieval_success=retrieval_success,
            fallback_reason=fallback_reason
        )
