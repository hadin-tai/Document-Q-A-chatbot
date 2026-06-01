from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatRequest(BaseModel):
    document_id: str
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    document_id: str

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
