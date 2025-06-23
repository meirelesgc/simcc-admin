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


class Permission(BaseModel):
    permission_id: UUID
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CreateUserRole(BaseModel):
    user_id: UUID
    role_id: UUID
