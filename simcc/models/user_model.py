from datetime import datetime
from secrets import token_urlsafe
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUser(BaseModel):
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
    institution_id: Optional[UUID] = None

    linkedin: Optional[str] = None
    photo_url: Optional[str] = None
    lattes_id: Optional[str] = None

    permissions: list = []

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class UserResponse(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr

    provider: str = 'LOCAL'
    verify: bool = False
    institution_id: Optional[UUID] = None

    linkedin: Optional[str] = None
    photo_url: Optional[str] = None
    lattes_id: Optional[str] = None

    roles: list = []

    permissions: list = []
    model_config = ConfigDict(from_attributes=True)


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
