from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_model
from simcc.security import get_current_user
from simcc.services.features import notification_service

router = APIRouter()


@router.get('/notification')
async def notifications_get(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await notification_service.notifications_get(conn, current_user)
