from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserModel(BaseModel):
    displayName: Optional[str] = None
    email: EmailStr
    uid: str
    photoURL: Optional[HttpUrl] = None
    shib_id: Optional[str] = None
    shib_code: Optional[str] = None
    linkedin: Optional[str] = None
    provider: Optional[str] = None
    lattes_id: Optional[str] = None
    institution_id: Optional[str] = None

    birth_date: Optional[str] = None
    course_level: Optional[str] = None
    first_name: Optional[str] = None
    registration: Optional[str] = None
    gender: Optional[str] = None
    last_name: Optional[str] = None
    email_status: Optional[str] = None
    visible_email: Optional[bool] = None


class FeedbackSchema(BaseModel):
    name: str = Field(
        ..., max_length=100, min_length=3, description="Full name of the user"
    )
    email: EmailStr
    rating: int = Field(..., ge=0, le=10, description="Rating between 0 and 10")
    description: Optional[str] = Field(
        None, description="Optional feedback description"
    )
