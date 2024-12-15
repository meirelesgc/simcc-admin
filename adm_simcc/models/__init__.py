from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserModel(BaseModel):
    displayName: str
    email: EmailStr
    uid: str = None
    photoURL: Optional[HttpUrl] = None
    shib_id: Optional[str] = None
    shib_code: Optional[str] = None
    linkedin: Optional[str] = None
    provider: Optional[str] = None
    lattes_id: Optional[str] = None


class FeedbackSchema(BaseModel):
    name: str = Field(
        ..., max_length=100, min_length=3, description="Full name of the user"
    )
    email: EmailStr
    rating: int = Field(..., ge=0, le=10, description="Rating between 0 and 10")
    description: Optional[str] = Field(
        None, description="Optional feedback description"
    )
