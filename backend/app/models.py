# backend/app/models.py
from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: str  # client-provided or generated UUID
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    escalate: bool = False
    suggestions: Optional[List[str]] = None

class FAQItem(BaseModel):
    id: str
    question: str
    answer: str
    tags: Optional[List[str]] = []
