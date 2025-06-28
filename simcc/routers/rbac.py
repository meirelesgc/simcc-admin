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
async def role_post(
    role: rbac_model.CreateRole,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.post_role(conn, role)


@router.post('/role/permissions/')
async def role_permissions_post(
    role_permission: rbac_model.CreateRolePermission,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.post_role_permissions(conn, role_permission)


@router.get('/role/', response_model=list[rbac_model.RoleResponse])
async def role_get(
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_role(conn, None)


@router.get('/role/{id}/', response_model=rbac_model.RoleResponse)
async def role_id_get(
    id: UUID,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_role(conn, id)


@router.get('/s/permission', deprecated=True)
@router.get(
    '/role/{role_id}/permission/',
    response_model=list[rbac_model.Permission],
)
async def role_permission_get(
    role_id: UUID,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_permissions(conn, role_id)


@router.put(
    '/role/',
    response_model=rbac_model.Role,
)
async def role_put(
    role: rbac_model.Role,
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.put_role(conn, role)


@router.delete(
    '/role/{role_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def role_delete(
    role_id: UUID,
    conn: Connection = Depends(get_conn),
):
    await rbac_service.delete_role(conn, role_id)


@router.get('/permission/', response_model=list[rbac_model.Permission])
async def permissions_get(
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_permissions(conn)
