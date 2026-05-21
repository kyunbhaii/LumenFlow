from pydantic import BaseModel, ConfigDict
from datetime import datetime

class KBDocumentBase(BaseModel):
    source: str
    content: str

class KBDocumentCreate(KBDocumentBase):
    """Schema for validating raw document uploads/ingestion."""
    pass

class KBDocumentResponse(KBDocumentBase):
    """Schema for serializing SQL database records back to the API."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)