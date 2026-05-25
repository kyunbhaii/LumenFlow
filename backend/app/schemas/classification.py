from pydantic import BaseModel, Field
from typing import Optional

class ClassificationResult(BaseModel):
    category: str = Field(description="The category of the ticket, e.g., 'Billing', 'Technical', 'Account', 'General'")
    priority: str = Field(description="The priority of the ticket: 'low', 'medium', 'high', 'urgent'")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    sentiment: Optional[str] = Field(default=None, description="The customer's emotional tone, e.g., 'neutral', 'angry', 'frustrated'")
    reasoning: Optional[str] = Field(default=None, description="Brief reasoning for this classification")