from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import UUID4, BaseModel, Field


class CreateCollection(BaseModel):
    name: str
    description: str


class Collection(BaseModel):
    collection_id: UUID4 = Field(default_factory=uuid4)
    name: str
    description: str

    visible: bool = False

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class CollectionEntry(BaseModel):
    collection_id: UUID
    entry_id: UUID
    type: str
