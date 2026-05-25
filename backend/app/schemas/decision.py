from typing import Optional
from pydantic import BaseModel


class DecisionResult(BaseModel):
    decision: str

    reason: str

    fallback_triggered: bool

    fallback_reason: Optional[str] = None