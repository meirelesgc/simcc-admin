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
    params = {}
    filters = str()

    if institution_id:
        params['institution_id'] = institution_id
        filters += 'AND i.institution_id = %(institution_id)s'

    SCRIPT_SQL = f"""
        WITH researcher_count AS (
            SELECT institution_id, COUNT(DISTINCT researcher_id)
                AS count_r
            FROM researcher
            GROUP BY institution_id
        ),
        graduate_program_count AS (
            SELECT institution_id, COUNT(DISTINCT graduate_program_id)
                AS count_gp
            FROM graduate_program
            GROUP BY institution_id
        ),
        graduate_program_researcher_count AS (
            SELECT gp.institution_id, SUM(gpr.count_r) AS count_gpr
            FROM graduate_program gp
            LEFT JOIN (
                SELECT graduate_program_id, COUNT(DISTINCT researcher_id)
                    AS count_r
                FROM graduate_program_researcher
                GROUP BY graduate_program_id
            ) gpr ON gpr.graduate_program_id = gp.graduate_program_id
            GROUP BY gp.institution_id
        ),
        graduate_program_student_count AS (
            SELECT gp.institution_id, SUM(gps.count_s) AS count_gps
            FROM graduate_program gp
            LEFT JOIN (
                SELECT graduate_program_id, COUNT(DISTINCT researcher_id)
                    AS count_s
                FROM graduate_program_student
                GROUP BY graduate_program_id
            ) gps ON gps.graduate_program_id = gp.graduate_program_id
            GROUP BY gp.institution_id
        ),
        ufmg_researcher_count AS (
            SELECT r.institution_id, COUNT(ur.researcher_id) AS count_d
            FROM ufmg.researcher ur
            LEFT JOIN researcher r ON r.researcher_id = ur.researcher_id
            GROUP BY r.institution_id
        ),
        technician_count AS (
            SELECT COUNT(*) AS count_t FROM ufmg.technician
        ),
        researchers AS (
            SELECT ARRAY_AGG(r.lattes_id) AS researchers_list, r.institution_id
            FROM researcher r
            GROUP BY r.institution_id
        )
        SELECT i.name, i.institution_id, COALESCE(r.count_r, 0) AS count_r,
            COALESCE(gp.count_gp, 0) AS count_gp, COALESCE(gpr.count_gpr, 0)
            AS count_gpr, COALESCE(gps.count_gps, 0) AS count_gps,
            COALESCE(d.count_d, 0) AS count_d, COALESCE(t.count_t, 0)
            AS count_t, i.acronym, COALESCE(rl.researchers_list, ARRAY[]::TEXT[]) AS researchers_list
        FROM institution i
            LEFT JOIN researcher_count r
                ON r.institution_id = i.institution_id
            LEFT JOIN graduate_program_count gp
                ON gp.institution_id = i.institution_id
            LEFT JOIN graduate_program_researcher_count gpr
                ON gpr.institution_id = i.institution_id
            LEFT JOIN graduate_program_student_count gps
                ON gps.institution_id = i.institution_id
            LEFT JOIN ufmg_researcher_count d
                ON d.institution_id = i.institution_id
            LEFT JOIN researchers rl
                ON rl.institution_id = i.institution_id
            CROSS JOIN technician_count t
        WHERE 1 = 1
            {filters}
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
