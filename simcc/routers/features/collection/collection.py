from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.schemas.features import collection_models
from simcc.security import get_current_user
from simcc.services.features import collection_service

router = APIRouter(prefix='/collection')

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=collection_models.Collection,
)
async def collection_post(
    collection: collection_models.CreateCollection,
    current_user: CurrentUser,
    conn: Conn,
):
    return await collection_service.post_collection(
        conn, collection, current_user
    )


@router.get(
    '/',
    response_model=list[collection_models.Collection],
)
async def collection_get(
    conn: Conn,
    current_user: CurrentUser,
):
    return await collection_service.get_collection(conn, current_user)


@router.get(
    '/{collection_id}/',
    response_model=collection_models.Collection,
)
async def collection_id_get(
    collection_id: UUID,
    conn: Conn,
    current_user: CurrentUser,
):
    collection = await collection_service.get_collection_by_id(
        conn, collection_id, current_user
    )
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Collection not found'
        )
    return collection


@router.get(
    '/public/{user_id}/',
    response_model=list[collection_models.Collection],
)
async def collection_public_get(user_id: UUID, conn: Conn):
    return await collection_service.get_public_collections(conn, user_id)


@router.put(
    '/',
    response_model=collection_models.Collection,
)
async def collection_put(
    collection: collection_models.Collection,
    current_user: CurrentUser,
    conn: Conn,
):
    return await collection_service.update_collection(
        conn, collection, current_user
    )


@router.delete(
    '/{collection_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def collection_delete(
    collection_id: UUID,
    current_user: CurrentUser,
    conn: Conn,
):
    await collection_service.delete_collection(
        conn, collection_id, current_user
    )


@router.post(
    '/{collection_id}/entries/',
    status_code=HTTPStatus.CREATED,
    response_model=collection_models.CollectionEntry,
)
async def collection_entries_post(
    collection_id: UUID,
    entry: collection_models.CreateCollectionEntry,
    current_user: CurrentUser,
    conn: Conn,
):
    return await collection_service.post_entries(
        conn,
        collection_id=collection_id,
        entry=entry,
        user=current_user,
    )


@router.get(
    '/{collection_id}/entries/',
    response_model=list[collection_models.CollectionEntry],
)
async def collection_entries_get(
    collection_id: UUID,
    conn: Conn,
    current_user: CurrentUser,
):
    entries = await collection_service.get_entries(
        conn, collection_id, current_user
    )
    if not entries:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Collection not found or permission denied',
        )
    return entries


@router.delete(
    '/{collection_id}/entries/{entry_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def collection_entries_delete(
    collection_id: UUID,
    entry_id: UUID,
    current_user: CurrentUser,
    conn: Conn,
):
    success = await collection_service.delete_entries(
        conn,
        collection_id=collection_id,
        entry_id=entry_id,
        user=current_user,
    )
    if not success:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Entry or collection not found, or permission denied',
        )
