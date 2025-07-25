from uuid import UUID

from simcc.core.connection import Connection
from simcc.models.features import star_models


async def create_star(conn: Connection, star: star_models.Star):
    params = star.model_dump()
    SCRIPT_SQL = """
        INSERT INTO feature.stars (user_id, entry_id, type)
        VALUES (%(user_id)s, %(entry_id)s, %(type)s)
        RETURNING user_id, entry_id, type
    """
    return await conn.select(SCRIPT_SQL, params, one=True)


async def get_stars_by_user_id(conn: Connection, user_id: UUID) -> list[dict]:
    params = {'user_id': user_id}
    SCRIPT_SQL = """
        SELECT user_id, entry_id, type
        FROM feature.stars
        WHERE user_id = %(user_id)s
    """
    return await conn.select(SCRIPT_SQL, params)


async def get_star_by_user_and_entry(
    conn: Connection, user_id: UUID, entry_id: UUID
) -> dict | None:
    params = {'user_id': user_id, 'entry_id': entry_id}
    SCRIPT_SQL = """
        SELECT user_id, entry_id, type
        FROM feature.stars
        WHERE user_id = %(user_id)s AND entry_id = %(entry_id)s
    """
    return await conn.select(SCRIPT_SQL, params, one=True)


async def delete_star(conn: Connection, user_id: UUID, entry_id: UUID) -> int:
    params = {'user_id': user_id, 'entry_id': entry_id}
    SCRIPT_SQL = """
        DELETE FROM feature.stars
        WHERE user_id = %(user_id)s AND entry_id = %(entry_id)s
    """
    return await conn.exec(SCRIPT_SQL, params)
