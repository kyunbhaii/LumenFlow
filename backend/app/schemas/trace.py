from datetime import datetime
from typing import Optional, Any
import json
from pydantic import BaseModel, ConfigDict, field_validator

class TraceBase(BaseModel):
    trace_id: str
    ticket_id: int
    node_name: str
    input_payload: Optional[str] = None
    output_payload: Optional[str] = None
    latency_ms: Optional[int] = None
    prompt_version: Optional[str] = None
    processing_status: str = "SUCCESS"
    fallback_reason: Optional[str] = None
    error_message: Optional[str] = None

    @field_validator("input_payload", "output_payload", mode="before")
    @classmethod
    def dict_to_json_string(cls, v: Any):
        if isinstance(v, dict):
            return json.dumps(v)
        if isinstance(v, list):
            return json.dumps(v)
        return v

class TraceCreate(TraceBase):
    pass

class TraceResponse(TraceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)