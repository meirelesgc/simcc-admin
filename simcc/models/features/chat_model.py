from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CreateMessage(BaseModel):
    content: str


class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)

    chat_id: UUID
    sender_id: UUID
    content: str

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
