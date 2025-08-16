from datetime import datetime
from secrets import token_urlsafe
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    password: str

    provider: str = 'LOCAL'
    verify: bool = False
    institution_id: UUID | None = None

    orcid_id: str | None = None
    linkedin: str | None = None
    photo_url: str | None = None
    lattes_id: str | None = None

    permissions: list = []
    roles: list = []

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class UserPublic(User):
    password: str = Field(exclude=True)
    created_at: datetime = Field(exclude=True)
    updated_at: datetime | None = Field(exclude=True)


class CreateKey(BaseModel):
    name: str


class Key(BaseModel):
    key_id: UUID = Field(default_factory=uuid4)
    name: str
    user_id: UUID
    key: str = Field(default_factory=lambda: token_urlsafe(32))
    created_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None


class KeyResponse(BaseModel):
    name: str
    key: str
    created_at: datetime
