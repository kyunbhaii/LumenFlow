from typing import List, Optional
from pydantic import BaseModel


class RetrievedDocument(BaseModel):
    source_id: str

    content: str
    
    similarity_score: float


class RetrievalResult(BaseModel):
    retrieved_docs: List[RetrievedDocument]

    retrieval_success: bool

    fallback_reason: Optional[str] = None