async def get_private_chat(conn, chat):
    user_ids = sorted(chat.users)
    params = {'cp1': user_ids[0], 'cp2': user_ids[1]}
    SCRIPT_SQL = """
        SELECT c.chat_id AS chat_id
        FROM feature.chats c
        JOIN feature.chat_participants cp1
            ON c.chat_id = cp1.chat_id AND cp1.user_id = %(cp1)s
        JOIN feature.chat_participants cp2
            ON c.chat_id = cp2.chat_id AND cp2.user_id = %(cp2)s
        WHERE c.is_group = FALSE;
        """
    return await conn.select(SCRIPT_SQL, params, True)


async def create_chat_record(conn, chat):
    params = chat.model_dump()
    query = """
        INSERT INTO feature.chats (chat_id, chat_name, is_group)
        VALUES (%(chat_id)s, %(chat_name)s, %(is_group)s)
        """
    return await conn.exec(query, params)


async def add_chat_participants(conn, chat):
    params = [{'p1': chat.chat_id, 'p2': u, 'p3': False} for u in chat.users]
    SCRIPT_SQL = """
        INSERT INTO feature.chat_participants (chat_id, user_id, is_admin)
        VALUES (%(p1)s, %(p2)s, %(p3)s)
        ON CONFLICT DO NOTHING;
        """
    await conn.executemany(SCRIPT_SQL, params)
