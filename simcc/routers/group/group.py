from http import HTTPStatus
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.schemas.group_schemas import GroupPublic, GroupSchema, GroupUpdate
from simcc.security import get_current_user
from simcc.services import group_service

router = APIRouter(prefix='/group')

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]


@router.post(
    '/researchGroupRest/Insert',
    include_in_schema=False,
    deprecated=True,
)
@router.post('/', response_model=GroupPublic, status_code=HTTPStatus.CREATED)
async def create_group(
    conn: Conn, current_user: CurrentUser, group: GroupSchema
):
    return await group_service.create_group(conn, group)


@router.get(
    '/researchGroupRest/Query',
    include_in_schema=False,
    deprecated=True,
)
@router.get('/', response_model=List[GroupPublic])
async def list_groups(
    conn: Conn,
    current_user: CurrentUser,
):
    return await group_service.list_groups(conn)


@router.get('/{group_id}', response_model=GroupPublic)
async def get_group(
    group_id,
    conn: Conn,
    current_user: CurrentUser,
):
    group = await group_service.list_groups(conn, group_id)
    if not group:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, 'Not found group with this id'
        )
    return group


@router.get(
    '/researchGroupRest/Update',
    include_in_schema=False,
    deprecated=True,
)
@router.put('/', response_model=GroupPublic)
async def update_group(
    conn: Conn, current_user: CurrentUser, group_update: GroupUpdate
):
    return await group_service.update_group(conn, group_update)


@router.get(
    '/researchGroupRest/Delete',
    include_in_schema=False,
    deprecated=True,
)
@router.delete('/{group_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_group(conn: Conn, current_user: CurrentUser, group_id: UUID):
    await group_service.delete_group(conn, group_id)
