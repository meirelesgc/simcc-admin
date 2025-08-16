from uuid import UUID

from pydantic import BaseModel


class CreateStar(BaseModel):
    entry_id: UUID
    type: str


class Star(BaseModel):
    user_id: UUID
    entry_id: UUID
    type: str
