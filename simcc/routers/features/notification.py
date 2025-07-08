from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_model
from simcc.models.features import notification_models
from simcc.security import get_current_user
from simcc.services.features import notification_service

router = APIRouter()


@router.get('/notification/')
async def notifications_get(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await notification_service.notifications_get(conn, current_user)


@router.post(
    '/notification/',
    response_model=notification_models.Notification,
    status_code=HTTPStatus.CREATED,
)
async def notification_post(
    notification: notification_models.CreateNotification,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await notification_service.notification_post(
        conn, current_user, notification
    )


@router.delete(
    '/notification/{notification_id}/', status_code=HTTPStatus.NO_CONTENT
)
async def notification_delete(
    notification_id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await notification_service.notification_delete(
        conn, notification_id
    )
