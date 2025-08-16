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


async def validate_link(conn, current_user, chat_id):
    SCRIPT_SQL = """
        SELECT 1
        FROM feature.chat_participants
        WHERE chat_id = %(chat_id)s
            AND user_id = %(user_id)s;
        """
    params = {'chat_id': chat_id, 'user_id': current_user.user_id}
    result = await conn.select(SCRIPT_SQL, params, True)
    return bool(result)


async def save_message(conn, message):
    params = message.model_dump()
    SCRIPT_SQL = """
        INSERT INTO feature.chat_messages (message_id, chat_id, sender_id,
            content, created_at)
        VALUES (%(message_id)s, %(chat_id)s, %(sender_id)s, %(content)s,
            %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_chats(conn, current_user):
    SCRIPT_SQL = """
        WITH last_messages AS (
            SELECT DISTINCT ON (cm.chat_id)
                cm.chat_id,
                row_to_json(cm.*) AS last_message
            FROM feature.chat_messages cm
            WHERE cm.deleted_at IS NULL
            ORDER BY cm.chat_id, cm.created_at DESC
        ), users_ AS (
            SELECT u.user_id, u.orcid_id, u.username, u.email, u.password, 
                u.provider, u.verify, u.institution_id, u.photo_url, u.lattes_id, 
                u.linkedin, u.created_at, u.updated_at
            FROM public.users u
            WHERE u.deleted_at IS NULL
        ), users AS (
            SELECT cp.chat_id, json_agg(row_to_json(u_.*)) AS users
            FROM feature.chat_participants cp
            LEFT JOIN users_ u_ ON u_.user_id = cp.user_id
            WHERE cp.deleted_at IS NULL
            GROUP BY cp.chat_id
        )
        SELECT 
            c.chat_id,
            c.chat_name,
            c.is_group,
            u.users,
            lm.last_message,
            c.created_at,
            c.updated_at
        FROM feature.chats c
        JOIN feature.chat_participants cp_filter
            ON cp_filter.chat_id = c.chat_id
            AND cp_filter.user_id = %(user_id)s
            AND cp_filter.deleted_at IS NULL
        LEFT JOIN last_messages lm ON lm.chat_id = c.chat_id
        LEFT JOIN users u ON u.chat_id = c.chat_id
        WHERE c.deleted_at IS NULL
        ORDER BY c.updated_at DESC;
        """
    return await conn.select(SCRIPT_SQL, {'user_id': current_user.user_id})
