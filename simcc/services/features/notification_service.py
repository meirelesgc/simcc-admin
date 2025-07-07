from simcc.models.features import notification_models
from simcc.repositories.features import notification_repository


async def notifications_get(conn, current_user):
    return await notification_repository.notifications_get(conn, current_user)


async def notification_post(conn, current_user, notification):
    notification = notification_models.Notification(
        **notification.model_dump(),
        sender_id=current_user.user_id,
    )
    print(notification)
