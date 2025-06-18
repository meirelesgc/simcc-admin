from datetime import datetime
from typing import Literal, Optional
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
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    role: Literal['ADMIN', 'DEFAULT']
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: Literal['ADMIN', 'DEFAULT']
    model_config = ConfigDict(from_attributes=True)
