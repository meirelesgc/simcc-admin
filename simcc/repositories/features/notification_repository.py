from psycopg.types.json import Jsonb


async def notifications_get(conn, current_user):
    params = current_user.model_dump()
    SCRIPT_SQL = """
        SELECT notification_id, user_id, sender_id, type, data, read,
            created_at, read_at
        FROM feature.notifications
        WHERE user_id = %(user_id)s;
        """
    return await conn.select(SCRIPT_SQL, params)


async def notification_post(conn, notification):
    params = notification.model_dump(mode='json')
    params['data'] = Jsonb(params['data'])
    if params['user_id'] == '*':
        SCRIPT_SQL = """
            INSERT INTO feature.notifications (user_id, sender_id, type, data,
                created_at)
            SELECT users.user_id, %(sender_id)s, %(type)s, %(data)s,
                %(created_at)s
            FROM users
        """
        return await conn.exec(SCRIPT_SQL, params)

    SCRIPT_SQL = """
        INSERT INTO feature.notifications (user_id, sender_id, type, data,
            created_at)
        VALUES (%(user_id)s, %(sender_id)s, %(type)s, %(data)s, %(created_at)s)
    """
    return await conn.exec(SCRIPT_SQL, params)


async def notification_delete(conn, notification_id):
    SCRIPT_SQL = """
        DELETE FROM feature.notifications
        WHERE notification_id = %(notification_id)s
    """
    params = {'notification_id': notification_id}
    return await conn.exec(SCRIPT_SQL, params)
