from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException

from simcc.core.connection import Connection
from simcc.models import user_model
from simcc.models.features import collection_models
from simcc.repositories.features import collection_repositoy


async def post_collection(
    conn: Connection,
    collection: collection_models.CreateCollection,
    current_user: user_model.User,
):
    collection = collection_models.Collection(**collection.model_dump())
    await collection_repositoy.post_collection(conn, collection, current_user)
    return collection


async def get_collection(conn: Connection, current_user: user_model.User):
    return await collection_repositoy.get_collection(conn, current_user)


async def get_public_collections(conn: Connection, user_id: UUID):
    return await collection_repositoy.get_public_collections(conn, user_id)


async def get_collection_by_id(
    conn: Connection, collection_id: UUID, current_user: user_model.User
):
    collection = await collection_repositoy.get_collection_by_id(
        conn, collection_id, current_user
    )

    return collection


async def update_collection(
    conn: Connection,
    collection: collection_models.Collection,
    current_user: user_model.User,
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
    conn: Connection, collection_id: UUID, current_user: user_model.User
):
    existing = await collection_repositoy.get_collection_by_id(
        conn, collection_id, current_user
    )
    if not existing:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Collection not found'
        )
    await collection_repositoy.delete_collection(conn, collection_id)


async def post_entries(
    conn: Connection,
    collection_id: UUID,
    entry: collection_models.CreateCollectionEntry,
    user: user_model.User,
):
    owner_collection = await collection_repositoy.get_collection_by_id(
        conn, collection_id, user
    )
    if not owner_collection:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Collection not found or permission denied',
        )

    entry = collection_models.CollectionEntry(
        collection_id=collection_id, **entry.model_dump()
    )
    await collection_repositoy.post_entries(conn, entry)
    return entry


async def get_entries(
    conn: Connection, collection_id: UUID, user: user_model.User
) -> list[collection_models.CollectionEntry] | None:
    collection = await collection_repositoy.get_any_collection_by_id(
        conn, collection_id
    )

    if not collection:
        return None
    if not collection['visible']:
        if collection['user_id'] != user.user_id:
            return None

    return await collection_repositoy.get_entries_by_collection_id(
        conn, collection_id
    )


async def delete_entries(
    conn: Connection,
    collection_id: UUID,
    entry_id: UUID,
    user: user_model.User,
) -> bool:
    owner_collection = await collection_repositoy.get_collection_by_id(
        conn, collection_id, user
    )
    if not owner_collection:
        return False

    deleted_rows = await collection_repositoy.delete_entries(
        conn, collection_id, entry_id
    )

    return deleted_rows > 0
