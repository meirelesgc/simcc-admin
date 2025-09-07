from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GroupSchema(BaseModel):
    name: str
    institution: Optional[str]
    first_leader: Optional[str]
    first_leader_id: Optional[UUID]
    second_leader: Optional[str]
    second_leader_id: Optional[UUID]
    area: Optional[str]
    census: Optional[int]
    start_of_collection: Optional[str]
    end_of_collection: Optional[str]
    group_identifier: str
    year: Optional[int]
    institution_name: Optional[str]
    category: Optional[str]


class GroupPublic(GroupSchema):
    id: UUID
    created_at: datetime = Field(..., default_factory=uuid4)
    updated_at: datetime = Field(..., default_factory=uuid4)
    deleted_at: Optional[datetime]


class GroupUpdate(BaseModel):
    id: UUID
    name: Optional[str] = None
    institution: Optional[str] = None
    first_leader: Optional[str] = None
    first_leader_id: Optional[UUID] = None
    second_leader: Optional[str] = None
    second_leader_id: Optional[UUID] = None
    area: Optional[str] = None
    census: Optional[int] = None
    start_of_collection: Optional[str] = None
    end_of_collection: Optional[str] = None
    group_identifier: Optional[str] = None
    year: Optional[int] = None
    institution_name: Optional[str] = None
    category: Optional[str] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
