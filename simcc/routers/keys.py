from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.security import (
    get_current_user,
)
from simcc.services import user_service

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]

router = APIRouter()


@router.post(
    '/key',
    response_model=user_model.KeyResponse,
    status_code=HTTPStatus.CREATED,
)
async def key_post(
    key: user_model.CreateKey,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await user_service.key_post(conn, current_user, key)


@router.get(
    '/key',
    response_model=list[user_model.KeyPublic],
)
async def key_get(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await user_service.key_get(conn, current_user)


@router.delete(
    '/key/{key_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def key_delete(
    key_id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    await user_service.key_delete(conn, key_id)
