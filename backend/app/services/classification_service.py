from typing import Optional
from sqlalchemy.orm import Session

from app.llm.reasoning_model import LLMClient
from app.llm.structured_output import ClassificationOutput
from app.observability.trace_logger import TraceLogger
from app.observability.trace_models import TraceCreate
from app.prompts.templates import build_classification_prompt


class ClassificationService:
    PROMPT_VERSION = "classify_v1"

    @staticmethod
    def classify(
        trace_id: str,
        ticket_id: int,
        subject: str,
        body: str,
        db: Optional[Session] = None
    ) -> ClassificationOutput:
        """
        Formats classification prompt via templates.py, categorizes the ticket using structured completion,
        and logs full pipeline metrics directly to PostgreSQL and the evaluation log.
        """
        start_time = TraceLogger.start_timer()
        error_msg = None
        fallback_reason = None

        try:
            # 1. Format classification prompt with variables
            prompt_template = build_classification_prompt()
            formatted_messages = prompt_template.format_messages(subject=subject, body=body)

            system_prompt = formatted_messages[0].content
            user_prompt = formatted_messages[1].content

            # 2. Query LLM for structured output matching ClassificationOutput
            output: ClassificationOutput = LLMClient.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="llama3-8b-8192",
                response_model=ClassificationOutput
            )
        except Exception as e:
            error_msg = str(e)
            # Default fallback output on critical processing error
            output = ClassificationOutput(
                category="General",
                priority="medium",
                confidence=0.0,
                sentiment="neutral",
                reasoning=f"LLM processing failed: {error_msg}"
            )
            fallback_reason = f"LLM Exception: {error_msg}"

        latency_ms = TraceLogger.end_timer(start_time)
        
        # 3. Log results to SQL & JSONL traces
        event = TraceCreate(
            trace_id=trace_id,
            ticket_id=ticket_id,
            node_name="classification_service",
            input_payload={"subject": subject, "body": body},
            output_payload=output.model_dump(),
            latency_ms=int(latency_ms),
            prompt_version=ClassificationService.PROMPT_VERSION,
            processing_status="SUCCESS" if not error_msg else "FAILED",
            fallback_reason=fallback_reason,
            error_message=error_msg
        )
        if db:
            TraceLogger.log_event(db, event)

        return output