async def post_role(conn, role):
    params = role.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.roles (role_id, name, created_at)
        VALUES (%(role_id)s, %(name)s, %(created_at)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_role(conn, role_id):
    one = False
    params = {}
    filters = str()

    if role_id:
        one = True
        params['role_id'] = role_id
        filters += 'AND role_id = %(role_id)s'

    SCRIPT_SQL = f"""
        WITH users_ AS (
            SELECT u.user_id, JSONB_BUILD_OBJECT(
                'user_id', u.user_id,
                'username', u.username
            ) AS user
            FROM users u
        )
        SELECT r.role_id, r.name, r.created_at, r.updated_at, ARRAY_AGG(u.user)
            AS users
        FROM public.roles r
            LEFT JOIN user_roles ur
                ON ur.role_id = r.role_id
            LEFT JOIN users_ u
                ON u.user_id = ur.user_id
        WHERE 1 = 1
            {filters}
        GROUP BY r.role_id
        """
    return await conn.select(SCRIPT_SQL, params, one)


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


async def get_permissions(conn, role_id):
    params = {}
    join_role_permission = str()
    filters = str()

    if role_id:
        params['role_id'] = role_id
        filters += 'AND rp.role_id = %(role_id)s'
        join_role_permission = """
            LEFT JOIN role_permissions rp
                ON rp.permission_id = p.permission_id
            """

    SCRIPT_SQL = f"""
        SELECT p.permission_id AS id, p.name AS permission, p.created_at,
            p.updated_at
        FROM public.permissions p
            {join_role_permission}
        WHERE 1 = 1
            {filters}
        """
    return await conn.select(SCRIPT_SQL, params)


async def post_user_role(conn, user_role):
    params = user_role.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.user_roles (user_id, role_id)
        VALUES (%(user_id)s, %(role_id)s);
        """
    return await conn.exec(SCRIPT_SQL, params)


async def post_role_permissions(conn, role_permission):
    params = role_permission.model_dump()
    SCRIPT_SQL = """
        INSERT INTO public.role_permissions (role_id, permission_id)
        VALUES (%(role_id)s, %(permission_id)s);
        """
    return await conn.exec(SCRIPT_SQL, params)
