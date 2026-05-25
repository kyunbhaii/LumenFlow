import re
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import settings

from app.llm.reasoning_model import LLMClient
from app.schemas.guardrail import GuardrailResult
from app.observability.trace_logger import TraceLogger
from app.schemas.trace import TraceCreate
from app.prompts.templates import build_safety_prompt

# Production-grade Security Rules categorized by vulnerability risk
SECURITY_RULES = {
    "prompt_injection": [
        r"ignore\s+(all\s+)?previous\s+instructions?",
        r"system\s+prompt",
        r"developer\s+message",
        r"bypass\s+safety",
        r"disable\s+guardrails?"
    ],

    "sensitive_data_access": [
        r"admin\s+credentials?",
        r"access\s+keys?",
        r"api\s+tokens?",
        r"secret\s+keys?",
        r"reveal\s+(internal|hidden|secret)"
    ],

    "policy_exfiltration": [
        r"confidential\s+policies?",
        r"internal\s+documentation",
        r"private\s+workflows?"
    ]
}


class GuardrailService:
    PROMPT_VERSION = "guardrail_v1"

    @staticmethod
    def check_safety(
        trace_id: str,
        ticket_id: int,
        text: str,
        db: Optional[Session] = None
    ) -> GuardrailResult:
        """
        Runs advanced regex category checking followed by a lightweight LLM-based safety scan.
        Saves execution metrics via TraceLogger if db is provided.
        """
        start_time = TraceLogger.start_timer()
        is_safe = True
        reason = "Message passed safety checks"
        prompt_version = "heuristic_v1"
        error_msg = None
        fallback_reason = None

        # 1. Advanced Regex Heuristics (Fast, robust, category-aware)
        for category, patterns in SECURITY_RULES.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    is_safe = False
                    reason = f"regex_safety_violation_{category}"
                    latency_ms = TraceLogger.end_timer(start_time)
                    fallback_reason = (
                        f"Regex guardrail triggered | "
                        f"category={category} | "
                        f"pattern={pattern}"
                    )
                    
                    event = TraceCreate(
                        trace_id=trace_id,
                        ticket_id=ticket_id,
                        node_name="guardrail_service",
                        input_payload={"text": text},
                        output_payload={"is_safe": is_safe, "reason": reason},
                        latency_ms=int(latency_ms),
                        prompt_version=prompt_version,
                        processing_status="SUCCESS",
                        fallback_reason=fallback_reason,
                        error_message=error_msg
                    )
                    if db:
                        TraceLogger.log_event(db, event)
                    return GuardrailResult(is_safe=is_safe, reason=reason)

        # 2. Lightweight LLM Security Check
        prompt_version = GuardrailService.PROMPT_VERSION

        try:
            # Build and format the prompt using ChatPromptTemplate
            safety_prompt = build_safety_prompt()
            formatted_messages = safety_prompt.format_messages(text=text)
            
            system_prompt = formatted_messages[0].content
            user_prompt = formatted_messages[1].content

            output: GuardrailResult = LLMClient.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=settings.REASONING_MODEL,
                response_model=GuardrailResult
            )
            is_safe = output.is_safe
            reason = output.reason
            
        except Exception as e:
            error_msg = str(e)
            # Default to safe on exception but mark fallback triggered
            is_safe = True
            reason = "safe_fallback_on_llm_failure"
            fallback_reason = f"LLM exception: {error_msg}"

        latency_ms = TraceLogger.end_timer(start_time)
        event = TraceCreate(
            trace_id=trace_id,
            ticket_id=ticket_id,
            node_name="guardrail_service",
            input_payload={"text": text},
            output_payload={"is_safe": is_safe, "reason": reason},
            latency_ms=int(latency_ms),
            prompt_version=prompt_version,
            processing_status="SUCCESS" if not error_msg else "FAILED",
            fallback_reason=fallback_reason,
            error_message=error_msg
        )
        if db:
            TraceLogger.log_event(db, event)

        return GuardrailResult(
            is_safe=is_safe,
            reason=reason
        )