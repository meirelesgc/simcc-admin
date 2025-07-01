from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class Notification(BaseModel):
    notification_id: UUID
    user_id: UUID
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
    read: bool
    created_at: datetime
    read_at: Optional[datetime]
