from simcc.repositories.features import notification_repository


async def notifications_get(conn, current_user):
    return await notification_repository.notifications_get(conn, current_user)
