async def researcher_post(conn, researchers: list):
    params = [r.model_dump(mode='json') for r in researchers]
    SCRIPT_SQL = """
        INSERT INTO public.researcher
        (researcher_id, name, lattes_id, institution_id) VALUES
        (%(researcher_id)s, %(name)s, %(lattes_id)s, %(institution_id)s);
    """
    await conn.executemany(SCRIPT_SQL, params)


async def researcher_get(conn, institution_id, name):
    params = {}
    filters = str()
    if institution_id:
        params['institution_id'] = institution_id
        filters += 'AND r.institution_id = %(institution_id)s'

    if name:
        params['name'] = name + '%'
        filters += 'AND r.name LIKE %(name)s'

    SCRIPT_SQL = f"""
        SELECT r.researcher_id, r.name, r.lattes_id, r.institution_id,
            r.status, r.created_at, r.updated_at, r.deleted_at
        FROM public.researcher r
        WHERE 1 = 1
            AND deleted_at IS NULL
            {filters}
        ORDER BY
            r.created_at DESC
        """
    return await conn.select(SCRIPT_SQL, params)


async def researcher_put(conn, researcher):
    params = researcher.model_dump()
    SCRIPT_SQL = """
        UPDATE public.researcher SET
            name=%(name)s,
            lattes_id=%(lattes_id)s,
            status=%(status)s,
            updated_at=%(updated_at)s
        WHERE researcher_id = %(researcher_id)s;
    """
    await conn.exec(SCRIPT_SQL, params)


async def researcher_delete(conn, researcher_id):
    SCRIPT_SQL = """
        UPDATE public.researcher
            SET deleted_at = now()
        WHERE researcher_id = %(researcher_id)s;
    """
    await conn.exec(SCRIPT_SQL, {'researcher_id': researcher_id})
