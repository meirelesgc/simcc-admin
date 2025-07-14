from uuid import uuid4


async def get_chat_id(conn, users):
    one = True
    params = {'chat_name': ':'.join(users)}
    SCRIPT_SQL = """
        SELECT chat_id
        FROM feature.chats
        WHERE chat_name = %(chat_name)s
            AND deleted_at IS NULL
            AND is_group = False
        """
    chat_id = await conn.select(SCRIPT_SQL, params, one)
    if chat_id and 'chat_id' in chat_id:
        return chat_id.get('chat_id')

    params['chat_id'] = uuid4()
    SCRIPT_SQL = """
        INSERT INTO feature.chats (chat_id, chat_name, is_group)
        VALUES (%(chat_id)s, %(chat_name)s, False);
        """
    await conn.exec(SCRIPT_SQL, params)
    return params['chat_id']


async def post_chat(conn, chat_id, sender_id, content):
    params = {'chat_id': chat_id, 'sender_id': sender_id, 'content': content}
    SCRIPT_SQL = """
        INSERT INTO feature.messages (chat_id, sender_id, content)
        VALUES (%(chat_id)s, %(sender_id)s, %(content)s);
        """
    await conn.exec(SCRIPT_SQL, params)
