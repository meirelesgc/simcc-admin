from uuid import UUID


async def create_group(conn, group):
    SCRIPT_SQL = """
        INSERT INTO research_group (id, name, institution, first_leader,
            first_leader_id, second_leader, second_leader_id, area, census,
            start_of_collection, end_of_collection, group_identifier, year,
            institution_name, category, created_at, updated_at, deleted_at)
        VALUES (%(id)s, %(name)s, %(institution)s, %(first_leader)s,
            %(first_leader_id)s, %(second_leader)s, %(second_leader_id)s,
            %(area)s, %(census)s, %(start_of_collection)s,
            %(end_of_collection)s, %(group_identifier)s, %(year)s,
            %(institution_name)s, %(category)s, %(created_at)s, %(updated_at)s,
            %(deleted_at)s)
        """
    await conn.exec(SCRIPT_SQL, group)


async def list_groups(conn, group_id=None):
    FILTERS = str()
    params = {}
    one = False
    if group_id:
        one = True
        params['group_id'] = group_id
        FILTERS += ' AND id = %(group_id)s'

    SCRIPT_SQL = f"""
        SELECT id, name, institution, first_leader, first_leader_id,
            second_leader, second_leader_id, area, census, start_of_collection,
            end_of_collection, group_identifier, year, institution_name,
            category, created_at, updated_at, deleted_at
        FROM research_group
        WHERE deleted_at IS NULL
            {FILTERS}
        ORDER BY created_at DESC
        """
    return await conn.select(SCRIPT_SQL, params, one)


async def update_group(conn, group_update):
    set_clauses = ', '.join([
        f'{key} = %({key})s' for key in group_update if key != 'group_id'
    ])
    SCRIPT_SQL = f"""
        UPDATE research_group
        SET {set_clauses}
        WHERE id = %(id)s
    """
    await conn.exec(SCRIPT_SQL, group_update)


async def delete_group(conn, group_id: UUID, deleted_at):
    params = {'group_id': group_id, 'deleted_at': deleted_at}
    SCRIPT_SQL = """
        UPDATE research_group
        SET deleted_at = %(deleted_at)s
        WHERE id = %(group_id)s
    """
    await conn.exec(SCRIPT_SQL, params)
