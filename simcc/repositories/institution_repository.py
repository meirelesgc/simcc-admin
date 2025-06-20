from simcc.core.connection import Connection


async def post_institution(institutions, conn: Connection):
    SCRIPT_SQL = """
        INSERT INTO public.institution (institution_id, name, acronym,
            created_at)
        VALUES (%(institution_id)s, %(name)s, %(acronym)s, %(created_at)s)
        """
    params = [i.model_dump(mode='json') for i in institutions]
    return await conn.executemany(SCRIPT_SQL, params)


async def get_institution(institution_id, conn: Connection):
    params = {'institution_id': institution_id}
    SCRIPT_SQL = """
        SELECT institution_id, name, acronym, lattes_id, created_at,
               updated_at, deleted_at
        FROM public.institution
        WHERE institution_id = %(institution_id)s
        AND deleted_at IS NULL;
    """
    return await conn.select(SCRIPT_SQL, params, one=True)


async def put_institution(institution, conn: Connection):
    SCRIPT_SQL = """
        UPDATE public.institution
        SET name = %(name)s,
            acronym = %(acronym)s,
            updated_at = %(updated_at)s
        WHERE institution_id = %(institution_id)s
        AND deleted_at IS NULL
        """
    return await conn.exec(SCRIPT_SQL, institution.model_dump(mode='json'))


async def delete_institution(institution_id, conn: Connection):
    params = {'institution_id': institution_id}
    SCRIPT_SQL = """
        UPDATE public.institution
        SET deleted_at = NOW()
        WHERE institution_id = %(institution_id)s
        AND deleted_at IS NULL;
        """
    return await conn.exec(SCRIPT_SQL, params)
