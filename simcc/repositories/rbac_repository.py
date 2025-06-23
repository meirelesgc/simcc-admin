from uuid import UUID


async def post_role(conn, role):
    params = role.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.roles (role_id, name, created_at)
        VALUES (%(role_id)s, %(name)s, %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_role(conn):
    SCRIPT_SQL = """
        SELECT role_id, name, created_at, updated_at
        FROM public.roles;
        """
    return await conn.select(SCRIPT_SQL)


async def get_role_id(conn, role_id: UUID):
    params = {'role_id': role_id}
    SCRIPT_SQL = """
        SELECT role_id, name, created_at, updated_at
        FROM public.roles;
        """
    return await conn.select(SCRIPT_SQL, params)


async def put_role(conn, role):
    params = role.model_dump()
    SCRIPT_SQL = """
        UPDATE public.roles
        SET name = %(name)s,
            updated_at = %(updated_at)s
        WHERE role_id = %(role_id)s;
        """
    return await conn.exec(SCRIPT_SQL, params)


async def delete_role(conn, role_id):
    SCRIPT_SQL = """
        DELETE FROM public.roles
        WHERE role_id = %(role_id)s;
        """
    await conn.exec(SCRIPT_SQL, {'role_id': role_id})


async def get_permissions(conn):
    SCRIPT_SQL = """
        SELECT permission_id, name, created_at, updated_at
        FROM public.permissions;
        """
    return await conn.select(SCRIPT_SQL)


async def post_user_role(conn, user_role):
    params = user_role.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.user_roles (user_id, role_id)
        VALUES (%(user_id)s, %(role_id)s);
        """
    return await conn.exec(SCRIPT_SQL, params)
