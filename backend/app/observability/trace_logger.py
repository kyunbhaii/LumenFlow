import json
import logging
import os
import time

from datetime import datetime
from typing import Optional, Any

from sqlalchemy.orm import Session

from app.db.models.trace import Trace
from app.observability.trace_models import TraceCreate


TRACE_FILE = "evals/traces.jsonl"

os.makedirs("evals", exist_ok=True)

logger = logging.getLogger("lumenflow.traces")

logger.setLevel(logging.INFO)


class TraceLogger:

    @staticmethod
    def start_timer() -> float:
        return time.time()

    @staticmethod
    def end_timer(start_time: float) -> float:
        return (time.time() - start_time) * 1000.0

    @staticmethod
    def log_event(
        db: Session,
        event: TraceCreate
    ) -> Trace:

        # -------------------------
        # Save to PostgreSQL
        # -------------------------

        trace = Trace(
            trace_id=event.trace_id,
            ticket_id=event.ticket_id,
            node_name=event.node_name,
            input_payload=event.input_payload,
            output_payload=event.output_payload,
            latency_ms=event.latency_ms,
            prompt_version=event.prompt_version,
            processing_status=event.processing_status,
            fallback_reason=event.fallback_reason,
            error_message=event.error_message
        )

        db.add(trace)
        db.commit()
        db.refresh(trace)

        # Structured terminal logs

        if event.error_message:
            logger.error(
                f"[TRACE:{event.trace_id}] "
                f"{event.node_name} failed"
            )
        else:
            logger.info(
                f"[TRACE:{event.trace_id}] "
                f"{event.node_name} completed "
                f"in {event.latency_ms}ms"
            )
        
        # JSONL evaluation logs

        trace_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": event.trace_id,
            "ticket_id": event.ticket_id,
            "node_name": event.node_name,
            "latency_ms": event.latency_ms,
            "processing_status": event.processing_status,
            "fallback_reason": event.fallback_reason,
            "error_message": event.error_message,
            "prompt_version": event.prompt_version,
            "input_payload": event.input_payload,
            "output_payload": event.output_payload
        }

        with open(TRACE_FILE, "a") as f:
            f.write(json.dumps(trace_record) + "\n\n")
        
        return trace