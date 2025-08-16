from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.exceptions import ForbiddenException
from simcc.schemas import rbac_model, user_model
from simcc.security import get_current_user
from simcc.services import rbac_service, user_service

router = APIRouter()

ALLOWED = ['ADMIN']


@router.post(
    '/user/',
    status_code=HTTPStatus.CREATED,
    response_model=user_model.UserResponse,
)
async def post_user(
    user: user_model.CreateUser,
    conn: Connection = Depends(get_conn),
):
    return await user_service.post_user(conn, user)


@router.get(
    '/s/user/all',
    deprecated=True,
    include_in_schema=False,
)
@router.get(
    '/s/user/entrys',
    deprecated=True,
    include_in_schema=False,
)
@router.get(
    '/user/',
    response_model=list[user_model.UserResponse],
)
async def get_user(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    if not set(current_user.permissions) & set(ALLOWED):
        raise ForbiddenException
    return await user_service.get_user(conn)


@router.get('/s/user', response_model=user_model.UserResponse, deprecated=True)
@router.get('/user/my-self/', response_model=user_model.UserResponse)
async def get_me(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await user_service.get_user(conn, current_user.user_id)


@router.get(
    '/user/{id}/',
    response_model=user_model.UserResponse,
)
async def get_single_user(
    id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    has_permission = any(p in current_user.permissions for p in ALLOWED)
    is_self = current_user.user_id == id
    if not (has_permission or is_self):
        raise ForbiddenException
    return await user_service.get_user(conn, id)


@router.put(
    '/user/',
    response_model=user_model.User,
)
async def put_user(
    user: user_model.User,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    has_permission = any(p in current_user.permissions for p in ALLOWED)
    is_self = current_user.user_id == user.user_id
    if not (has_permission or is_self):
        raise ForbiddenException
    return await user_service.put_user(conn, user)


@router.delete(
    '/user/{id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_user(
    id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    has_permission = any(p in current_user.permissions for p in ALLOWED)
    is_self = current_user.user_id == id
    if not (has_permission or is_self):
        raise ForbiddenException
    return await user_service.delete_user(conn, id)


@router.post(
    '/user/role/',
    status_code=HTTPStatus.CREATED,
)
async def user_role_post(
    user_role: rbac_model.CreateUserRole, conn: Connection = Depends(get_conn)
):
    return await rbac_service.post_user_role(conn, user_role)
