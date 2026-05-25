from pydantic import BaseModel, Field

class GuardrailResult(BaseModel):
    is_safe: bool = Field(description="True if the content passed safety checks, False if it was flagged.")
    reason: str = Field(description="Reasoning or description of why it was flagged as safe or unsafe.")