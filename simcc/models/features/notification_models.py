from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateNotification(BaseModel):
    type: Literal[
        'NEW_PRODUCTION',
        'USER_FOLLOWED',
        'PRODUCTION_LIKED',
        'LATTES_REMINDER',
        'ORCID_REMINDER',
        'NEW_LOGIN',
    ]
    data: dict
    user_id: UUID | Literal['*']


class Notification(BaseModel):
    notification_id: UUID
    user_id: UUID | Literal['*']
    sender_id: UUID
    type: Literal[
        'NEW_PRODUCTION',
        'USER_FOLLOWED',
        'PRODUCTION_LIKED',
        'LATTES_REMINDER',
        'ORCID_REMINDER',
        'NEW_LOGIN',
    ]
    data: dict
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    read_at: Optional[datetime]
