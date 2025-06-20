from uuid import UUID

from simcc.core.connection import Connection
from simcc.models import user_models
from simcc.models.features import collection_models


async def post_collection(
    conn: Connection,
    collection: collection_models.Collection,
    current_user: user_models.User,
):
    params = collection.model_dump()
    params['user_id'] = current_user.id
    SCRIPT_SQL = """
        INSERT INTO feature.collection (collection_id, user_id, name,
            description, visible)
        VALUES (%(collection_id)s, %(user_id)s, %(name)s, %(description)s,
            TRUE)
        """
    return await conn.exec(SCRIPT_SQL, params)


async def get_collection(conn: Connection, current_user: user_models.User):
    params = {'user_id': current_user.id}
    SCRIPT_SQL = """
        SELECT collection_id, name, description, visible
        FROM feature.collection
        WHERE user_id = %(user_id)s AND deleted_at IS NULL
        """
    return await conn.select(SCRIPT_SQL, params)


async def get_collection_by_id(
    conn: Connection, collection_id: UUID, current_user: user_models.User
):
    params = {'collection_id': collection_id, 'user_id': current_user.id}
    SCRIPT_SQL = """
        SELECT collection_id, name, description, visible
        FROM feature.collection
        WHERE collection_id = %(collection_id)s
          AND user_id = %(user_id)s
    """
    return await conn.select(SCRIPT_SQL, params, one=True)


async def update_collection(
    conn: Connection, collection: collection_models.Collection
):
    params = collection.model_dump()
    SCRIPT_SQL = """
        UPDATE feature.collection
        SET name = %(name)s,
            description = %(description)s,
            updated_at = %(updated_at)s
        WHERE collection_id = %(collection_id)s
    """
    return await conn.exec(SCRIPT_SQL, params)


async def delete_collection(conn: Connection, collection_id: UUID):
    params = {'collection_id': collection_id}
    SCRIPT_SQL = """
        UPDATE feature.collection
        SET visible = FALSE,
            deleted_at = now()
        WHERE collection_id = %(collection_id)s
    """
    return await conn.exec(SCRIPT_SQL, params)


async def get_public_collections(conn: Connection, user_id: UUID):
    params = {'user_id': user_id}
    SCRIPT_SQL = """
        SELECT collection_id, name, description
        FROM feature.collection
        WHERE user_id = %(user_id)s AND visible = TRUE
        """
    return await conn.select(SCRIPT_SQL, params)


async def post_collection_entries(conn, entry):
    params = entry.model_dump()
    SCRIPT_SQL = """
        INSERT INTO feature.collection_entries (collection_id, entrie_id, type)
        VALUES (%(collection_id)s, %(entrie_id)s, %(type)s)
        """
    return await conn.exec(SCRIPT_SQL, params)
