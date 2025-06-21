from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_models
from simcc.security import get_current_user
from simcc.services import user_service

router = APIRouter()


@router.post(
    '/user/',
    status_code=HTTPStatus.CREATED,
    response_model=user_models.UserResponse,
)
async def post_user(
    user: user_models.CreateUser,
    conn: Connection = Depends(get_conn),
):
    return await user_service.post_user(conn, user)


@router.get(
    '/user/',
    status_code=HTTPStatus.OK,
    response_model=list[user_models.UserResponse],
)
async def get_user(conn: Connection = Depends(get_conn)):
    return await user_service.get_user(conn)


@router.get(
    '/user/{id}/',
    status_code=HTTPStatus.OK,
    response_model=user_models.UserResponse,
)
async def get_single_user(id: UUID, conn: Connection = Depends(get_conn)):
    return await user_service.get_user(conn, id)


@router.put(
    '/user/',
    status_code=HTTPStatus.OK,
    response_model=user_models.User,
)
async def put_user(
    user: user_models.User,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    forbidden_exception = HTTPException(
        status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
    )
    if current_user.user_id != user.user_id and current_user.role != 'ADMIN':
        raise forbidden_exception
    if current_user.role == 'DEFAULT' and user.role == 'ADMIN':
        raise forbidden_exception

    return await user_service.put_user(conn, user)


@router.delete(
    '/user/{id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_user(
    id: UUID,
    current_user: user_models.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await user_service.delete_user(conn, id)
