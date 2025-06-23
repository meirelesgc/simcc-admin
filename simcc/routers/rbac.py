from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import rbac_model
from simcc.services import rbac_service

router = APIRouter()


@router.post(
    '/role/',
    status_code=HTTPStatus.CREATED,
    response_model=rbac_model.Role,
)
async def post_role(
    role: rbac_model.CreateRole,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.post_role(conn, role)


@router.get('/role/', response_model=list[rbac_model.RoleResponse])
async def get_role(
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_role(conn, None)


@router.get('/role/{id}/', response_model=rbac_model.RoleResponse)
async def get_role_id(
    id: UUID,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_role(conn, id)


@router.put(
    '/role/',
    response_model=rbac_model.Role,
)
async def put_role(
    role: rbac_model.Role,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.put_role(conn, role)


@router.delete(
    '/role/{role_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_role(
    role_id: UUID,
    conn: Connection = Depends(get_conn),
):
    await rbac_service.delete_role(conn, role_id)


@router.get('/permission/', response_model=list[rbac_model.Permission])
async def get_permissions(
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_permissions(conn)


@router.post(
    '/user/role/',
    status_code=HTTPStatus.CREATED,
)
async def post_user_role(
    user_role: rbac_model.CreateUserRole, conn: Connection = Depends(get_conn)
):
    return await rbac_service.post_user_role(conn, user_role)
