from uuid import uuid4


async def chat_message_get(conn, chat_id):
    params = {'chat_id': chat_id}
    SCRIPT_SQL = """
        SELECT message_id, chat_id, sender_id, content, created_at, updated_at
        FROM feature.messages
        WHERE chat_id = %(chat_id)s
        AND deleted_at IS NULL
        ORDER BY created_at ASC
        """
    return await conn.select(SCRIPT_SQL, params)


async def fetch_chat_id(conn, users):
    chat_name = ':'.join(users)
    params = {'chat_id': uuid4(), 'chat_name': chat_name}

    SCRIPT_SQL = """
        INSERT INTO feature.chats (chat_id, chat_name, is_group)
        VALUES (%(chat_id)s, %(chat_name)s, False)
        ON CONFLICT (chat_name, is_group) DO NOTHING;
        """
    await conn.exec(SCRIPT_SQL, params)

    SCRIPT_SQL = """
        SELECT chat_id
        FROM feature.chats
        WHERE chat_name = %(chat_name)s
            AND deleted_at IS NULL
            AND is_group = False;
        """
    chat = await conn.select(SCRIPT_SQL, {'chat_name': chat_name}, one=True)
    return chat['chat_id']


async def chat_message_post(conn, message):
    params = message.model_dump()
    SCRIPT_SQL = """
        INSERT INTO feature.messages (message_id, chat_id, sender_id, content,
            sent_at)
        VALUES (%(message_id)s, %(chat_id)s, %(sender_id)s, %(content)s,
            %(created_at)s);
        """
    await conn.exec(SCRIPT_SQL, params)
