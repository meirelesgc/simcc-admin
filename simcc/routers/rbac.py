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


@router.get('/role/', response_model=list[rbac_model.Role])
async def get_role(
    conn: Connection = Depends(get_conn),
):
    return await rbac_service.get_role(conn)


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
