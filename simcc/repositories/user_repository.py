from uuid import UUID

from pydantic import EmailStr

from simcc.core.connection import Connection
from simcc.models import user_model


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
):
    one = False
    params = {}
    filters = str()

    if user_id:
        one = True
        params['user_id'] = user_id
        filters += 'AND u.user_id = %(user_id)s'

    if email:
        one = True
        params['email'] = email
        filters += 'AND u.email = %(email)s'

    SCRIPT_SQL = f"""
        SELECT u.user_id, u.username, u.email, u.password, u.created_at,
            u.updated_at, ARRAY_AGG(r.name) AS roles, linkedin, photo_url,
            lattes_id
        FROM public.users u
            LEFT JOIN user_roles ur
                ON ur.user_id = u.user_id
            LEFT JOIN roles r
                ON r.role_id = ur.role_id
        WHERE 1 = 1
            {filters}
            {filters}
        GROUP BY u.user_id;
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
