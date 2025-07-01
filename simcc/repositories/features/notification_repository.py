async def notifications_get(conn, current_user):
    params = current_user.model_dump()
    SCRIPT_SQL = """
        SELECT notification_id, user_id, sender_id, type, data, read,
            created_at, read_at
        FROM notifications
        """
    return await conn.select(SCRIPT_SQL, params)
