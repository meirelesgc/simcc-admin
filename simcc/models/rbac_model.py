from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CreateRole(BaseModel):
    name: str


class Role(BaseModel):
    role_id: UUID = Field(default_factory=uuid4)
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
