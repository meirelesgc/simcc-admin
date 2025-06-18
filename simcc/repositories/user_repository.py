from uuid import UUID

from pydantic import EmailStr

from simcc.core.connection import Connection
from simcc.models import user_models


async def post_user(conn: Connection, user: user_models.User):
    params = user.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.users (id, username, email, role, password, created_at)
        VALUES (%(id)s, %(username)s, %(email)s, %(role)s, %(password)s, %(created_at)s);
        """  # noqa: E501
    return await conn.exec(SCRIPT_SQL, params)


async def get_user(conn: Connection, id: UUID = None, email: EmailStr = None):
    one = False
    params = {}

    filter_id = str()
    if id:
        one = True
        params['id'] = id
        filter_id = 'AND id = %(id)s'

    filter_email = str()
    if email:
        one = True
        params['email'] = email
        filter_email = 'AND email = %(email)s'

    SCRIPT_SQL = f"""
        SELECT id, username, email, role, password, created_at, updated_at
        FROM public.users
        WHERE 1 = 1
            {filter_id}
            {filter_email};
        """
    return await conn.select(SCRIPT_SQL, params, one)


async def put_user(conn: Connection, user: user_models.User):
    params = user.model_dump()
    SCRIPT_SQL = """
        UPDATE public.users
            SET username = %(username)s,
                email = %(email)s,
                password = %(password)s,
                updated_at = %(updated_at)s
        WHERE id = %(id)s;
        """
    return await conn.exec(SCRIPT_SQL, params)


async def delete_user(conn: Connection, id: UUID):
    params = {'id': id}
    SCRIPT_SQL = """
        DELETE FROM public.users
        WHERE id = %(id)s;
        """
    await conn.exec(SCRIPT_SQL, params)
