# researcher_model.py

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class CreateResearcher(BaseModel):
    name: str
    lattes_id: str
    institution_id: UUID


class UpdateResearcher(BaseModel):
    researcher_id: UUID
    name: str
    lattes_id: str
    status: bool
    institution_id: UUID


class ResearcherResponse(BaseModel):
    researcher_id: UUID = Field(default_factory=uuid4)
    name: str
    lattes_id: str
    institution_id: UUID
    status: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
