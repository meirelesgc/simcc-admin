from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_models
from simcc.models.features import collection_models
from simcc.security import get_current_user
from simcc.services.features import collection_service

router = APIRouter()


@router.post(
    '/collection/',
    status_code=HTTPStatus.CREATED,
    response_model=collection_models.Collection,
)
async def post_collection(
    collection: collection_models.CreateCollection,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await collection_service.post_collection(
        conn, collection, current_user
    )


@router.get(
    '/collection/',
    status_code=HTTPStatus.OK,
    response_model=list[collection_models.Collection],
)
async def get_collection(
    conn: Connection = Depends(get_conn),
    current_user: user_models.User = Depends(get_current_user),
):
    return await collection_service.get_collection(conn, current_user)


@router.get(
    '/collection/{collection_id}/',
    status_code=HTTPStatus.OK,
    response_model=collection_models.Collection,
)
async def get_collection_by_id(
    collection_id: UUID,
    conn: Connection = Depends(get_conn),
    current_user: user_models.User = Depends(get_current_user),
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
    '/collection/public/{user_id}/',
    status_code=HTTPStatus.OK,
    response_model=list[collection_models.Collection],
)
async def get_public_collections(
    user_id: UUID, conn: Connection = Depends(get_conn)
):
    return await collection_service.get_public_collections(conn, user_id)


@router.put(
    '/collection/',
    status_code=HTTPStatus.OK,
    response_model=collection_models.Collection,
)
async def update_collection(
    collection: collection_models.Collection,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await collection_service.update_collection(
        conn, collection, current_user
    )


@router.delete(
    '/collection/{collection_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_collection(
    collection_id: UUID,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    await collection_service.delete_collection(
        conn, collection_id, current_user
    )


@router.post(
    '/collection/entry/',
    status_code=HTTPStatus.CREATED,
)
async def post_collection_entry(
    entry: collection_models.CollectionEntry,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await collection_service.post_collection_entry(
        conn, entry, current_user
    )
