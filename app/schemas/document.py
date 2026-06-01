from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    file_name: str

class DocumentCreate(DocumentBase):
    pinecone_file_id: str
    user_id: str

class DocumentResponse(DocumentBase):
    id: str
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True
