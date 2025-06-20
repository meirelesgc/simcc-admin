from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field


class CreateInstitution(BaseModel):
    name: str
    acronym: str


class Institution(BaseModel):
    institution_id: UUID4 = Field(default_factory=uuid4)
    name: str
    acronym: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
