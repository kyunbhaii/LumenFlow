from pydantic import BaseModel, Field
from typing import List

class ClassificationOutput(BaseModel):
    category: str = Field(description="The category of the ticket, e.g., 'Billing', 'Technical', 'Account', 'General'")
    priority: str = Field(description="The priority of the ticket: 'low', 'medium', 'high', 'urgent'")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    sentiment: str = Field(description="The customer's emotional tone, e.g., 'neutral', 'angry', 'frustrated'")
    reasoning: str = Field(description="Brief reasoning for this classification")

class GuardrailOutput(BaseModel):
    is_safe: bool = Field(description="True if the prompt is safe, False if it contains injection or policy violations")
    reason: str = Field(description="Why it was flagged as safe or unsafe")

class DraftOutput(BaseModel):
    response: str = Field(description="The drafted response to the user")
    cited_sources: List[str] = Field(description="List of document IDs or titles used as evidence")