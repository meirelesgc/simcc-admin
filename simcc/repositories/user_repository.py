from uuid import UUID

from pydantic import EmailStr

from simcc.core.connection import Connection
from simcc.schemas import user_model


async def post_user(conn: Connection, user: user_model.User):
    params = user.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.users (user_id, username, email, password,
            provider, verify, created_at)
        VALUES (%(user_id)s, %(username)s, %(email)s, %(password)s,
            %(provider)s, %(verify)s, %(created_at)s);
        """  # noqa: E501
    return await conn.exec(SCRIPT_SQL, params)


async def get_user(
    conn: Connection,
    user_id: UUID = None,
    email: EmailStr = None,
    username: str = None,
):
    one = False
    params = {}
    filters = str()

    if user_id:
        one = True
        params['user_id'] = user_id
        filters += ' AND u.user_id = %(user_id)s'

    if email:
        one = True
        params['email'] = email
        filters += ' AND u.email = %(email)s'

    if username:
        params['username'] = username + '%'
        filters += ' AND u.username ILIKE %(username)s'

    SCRIPT_SQL = f"""
        WITH roles_ AS (
            SELECT ur.user_id, json_agg(row_to_json(r_)) AS roles
            FROM public.user_roles ur
            JOIN (SELECT r.role_id AS id, r.name AS role_id
                FROM public.roles r) r_ ON ur.role_id = r_.id
            GROUP BY ur.user_id
        ), permissions_ AS (
            SELECT u.user_id, ARRAY_REMOVE(ARRAY_AGG(DISTINCT p.name), NULL) AS
                permissions
            FROM public.users u
                LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                LEFT JOIN role_permissions rp ON rp.role_id = ur.role_id
                LEFT JOIN permissions p ON p.permission_id = rp.permission_id
            GROUP BY u.user_id
        ) SELECT u.user_id, u.username, u.email, u.password,
            u.created_at, u.updated_at,
            COALESCE(r.roles, '[]'::json) AS roles,
            COALESCE(p.permissions, ARRAY[]::text[]) AS permissions,
            linkedin, photo_url, lattes_id, institution_id, verify,
            provider, icon_url, cover_url
        FROM public.users u
        LEFT JOIN roles_ r
            ON r.user_id = u.user_id
        LEFT JOIN permissions_ p
            ON p.user_id = u.user_id
        WHERE 1 = 1
            {filters}
        """
    return await conn.select(SCRIPT_SQL, params, one)


async def put_user(conn: Connection, user: user_model.User):
    params = user.model_dump()
    SCRIPT_SQL = """
        UPDATE public.users
            SET username = %(username)s,
                email = %(email)s,
                password = %(password)s,
                updated_at = %(updated_at)s
        WHERE user_id = %(user_id)s;
        """
    return await conn.exec(SCRIPT_SQL, params)


async def delete_user(conn: Connection, user_id: UUID):
    params = {'user_id': user_id}
    SCRIPT_SQL = """
        DELETE FROM public.users
        WHERE user_id = %(user_id)s;
        """
    await conn.exec(SCRIPT_SQL, params)


async def key_post(conn: Connection, key):
    params = key.model_dump()
    SCRIPT_SQL = """
        INSERT INTO keys (key_id, user_id, key, created_at)
        VALUES (%(key_id)s, %(user_id)s, %(key)s, %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)
