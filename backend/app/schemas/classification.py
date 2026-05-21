from pydantic import BaseModel
from typing import Optional

class ClassificationResult(BaseModel):

    category: str

    priority: str

    confidence: float

    sentiment: Optional[str] = None

    reasoning: Optional[str] = None