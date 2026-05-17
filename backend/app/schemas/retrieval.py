from pydantic import BaseModel


class RetrievedDocument(BaseModel):
    source_id: str

    content: str

    similarity_score: float