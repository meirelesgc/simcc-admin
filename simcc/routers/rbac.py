from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import rbac_model, user_model
from simcc.security import get_current_user
from simcc.services import rbac_service

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]

ALLOWED_PERMISSIONS = {'ADMIN'}


async def admin_required(current_user: CurrentUser):
    user_permissions = set(current_user.permissions)
    if not user_permissions.intersection(ALLOWED_PERMISSIONS):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have enough permissions to perform this action.',
        )
    return current_user


router = APIRouter(dependencies=[Depends(admin_required)])


@router.post(
    '/role/', status_code=HTTPStatus.CREATED, response_model=rbac_model.Role
)
async def role_post(role: rbac_model.CreateRole, conn: Conn):
    return await rbac_service.post_role(conn, role)


@router.post('/role/permissions/')
async def role_permissions_post(
    role_permission: rbac_model.CreateRolePermission, conn: Conn
):
    return await rbac_service.post_role_permissions(conn, role_permission)


@router.get('/role/', response_model=list[rbac_model.RoleResponse])
async def role_get(conn: Conn):
    return await rbac_service.get_role(conn, None)


@router.get('/role/{id}/', response_model=rbac_model.RoleResponse)
async def role_id_get(id: UUID, conn: Conn):
    return await rbac_service.get_role(conn, id)


@router.get(
    '/role/{role_id}/permission/', response_model=list[rbac_model.Permission]
)
async def role_permission_get(role_id: UUID, conn: Conn):
    return await rbac_service.get_permissions(conn, role_id)


@router.put('/role/', response_model=rbac_model.Role)
async def role_put(role: rbac_model.Role, conn: Conn):
    return await rbac_service.put_role(conn, role)


@router.delete('/role/{role_id}/', status_code=HTTPStatus.NO_CONTENT)
async def role_delete(role_id: UUID, conn: Conn):
    await rbac_service.delete_role(conn, role_id)


@router.get('/permission/', response_model=list[rbac_model.Permission])
async def permissions_get(conn: Conn):
    return await rbac_service.get_permissions(conn, None)
