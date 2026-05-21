from pydantic import BaseModel, Field
from typing import List

class DraftResult(BaseModel):
    response: str = Field(description="The drafted polite, helpful support response to the customer.")
    cited_source: List[str] = Field(
        default=[],
        description="List of raw source IDs cited as evidence for the claims in the response."
    )