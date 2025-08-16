from simcc.repositories.features import notification_repository
from simcc.schemas.features import notification_models


async def notifications_get(conn, current_user):
    return await notification_repository.notifications_get(conn, current_user)


async def notification_post(conn, current_user, notification):
    notification = notification_models.Notification(
        **notification.model_dump(),
        sender_id=current_user.user_id,
    )
    await notification_repository.notification_post(conn, notification)
    return notification


async def notification_delete(conn, notification_id):
    return await notification_repository.notification_delete(
        conn, notification_id
    )
