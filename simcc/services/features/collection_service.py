from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException

from simcc.core.connection import Connection
from simcc.models import user_models
from simcc.models.features import collection_models
from simcc.repositories.features import collection_repositoy


async def post_collection(
    conn: Connection,
    collection: collection_models.CreateCollection,
    current_user: user_models.User,
):
    collection = collection_models.Collection(**collection.model_dump())
    await collection_repositoy.post_collection(conn, collection, current_user)
    return collection


async def get_collection(conn: Connection, current_user: user_models.User):
    return await collection_repositoy.get_collection(conn, current_user)


async def get_public_collections(conn: Connection, user_id: UUID):
    return await collection_repositoy.get_public_collections(conn, user_id)


async def get_collection_by_id(
    conn: Connection, collection_id: UUID, current_user: user_models.User
):
    collection = await collection_repositoy.get_collection_by_id(
        conn, collection_id, current_user
    )

    return collection


async def update_collection(
    conn: Connection,
    collection: collection_models.Collection,
    current_user: user_models.User,
):
    existing = await collection_repositoy.get_collection_by_id(
        conn, collection.collection_id, current_user
    )
    if not existing:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Collection not found'
        )
    collection.updated_at = datetime.now()
    await collection_repositoy.update_collection(conn, collection)
    return collection


async def delete_collection(
    conn: Connection, collection_id: UUID, current_user: user_models.User
):
    existing = await collection_repositoy.get_collection_by_id(
        conn, collection_id, current_user
    )
    if not existing:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Collection not found'
        )
    await collection_repositoy.delete_collection(conn, collection_id)


async def post_collection_entry(conn, entry, current_user):
    if await get_collection_by_id(conn, entry.collection_id, current_user):
        await delete_collection(conn, entry.collection_id, current_user)
    return await collection_repositoy.post_collection_entry(conn, entry)
