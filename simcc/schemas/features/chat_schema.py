from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    chat_name: str
    is_group: bool
    users: list


class Chat(BaseModel):
    chat_id: UUID = Field(default_factory=uuid4)
    chat_name: str
    is_group: bool
    users: list
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class ChatPubic(Chat):
    created_at: datetime = Field(exclude=True)
    updated_at: datetime | None = Field(exclude=True)
