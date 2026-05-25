from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings

from app.llm.reasoning_model import LLMClient
from app.schemas.draft import DraftResult
from app.schemas.retrieval import RetrievedDocument
from app.observability.trace_logger import TraceLogger
from app.schemas.trace import TraceCreate
from app.prompts.templates import build_draft_prompt, format_context_for_prompt


class DraftingService:
    PROMPT_VERSION = "draft_v1"

    @staticmethod
    def draft_response(
        trace_id: str,
        ticket_id: int,
        subject: str,
        body: str,
        retrieved_docs: List[RetrievedDocument],
        db: Optional[Session] = None
    ) -> DraftResult:
        """
        Formats retrieved guidelines, drafts a grounded support reply matching the DraftResult schema,
        and logs full pipeline metrics directly to PostgreSQL and the evaluation log.
        """
        start_time = TraceLogger.start_timer()
        error_msg = None
        fallback_reason = None

        try:
            # 1. Format context and create draft prompt
            formatted_context = format_context_for_prompt(retrieved_docs)
            prompt_template = build_draft_prompt()
            formatted_messages = prompt_template.format_messages(
                formatted_context=formatted_context,
                subject=subject,
                body=body
            )

            system_prompt = formatted_messages[0].content
            user_prompt = formatted_messages[1].content

            # 2. Query LLM for structured output matching DraftResult
            output: DraftResult = LLMClient.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=settings.REASONING_MODEL,
                response_model=DraftResult
            )
        except Exception as e:
            error_msg = str(e)
            # Default fallback output on critical processing error
            output = DraftResult(
                response="This request has been routed to a human specialist.",
                cited_sources=[]
            )
            fallback_reason = f"LLM Exception: {error_msg}"

        latency_ms = TraceLogger.end_timer(start_time)
        
        # 3. Log results to SQL & JSONL traces
        event = TraceCreate(
            trace_id=trace_id,
            ticket_id=ticket_id,
            node_name="drafting_service",
            input_payload={
                "subject": subject,
                "body": body,
                "retrieved_docs_count": len(retrieved_docs)
            },
            output_payload=output.model_dump(),
            latency_ms=int(latency_ms),
            prompt_version=DraftingService.PROMPT_VERSION,
            processing_status="SUCCESS" if not error_msg else "FAILED",
            fallback_reason=fallback_reason,
            error_message=error_msg
        )
        if db:
            TraceLogger.log_event(db, event)

        return output