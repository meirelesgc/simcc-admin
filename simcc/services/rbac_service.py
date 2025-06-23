from datetime import datetime
from uuid import UUID

from simcc.core.connection import Connection
from simcc.models import rbac_model
from simcc.repositories import rbac_repository


async def post_role(conn: Connection, role: rbac_model.CreateRole):
    role = rbac_model.Role(**role.model_dump())
    await rbac_repository.post_role(conn, role)
    return role


async def get_role(conn: Connection):
    return await rbac_repository.get_role(conn)


async def get_role_id(conn: Connection, id: UUID):
    return await rbac_repository.get_role_id(conn, id)


async def put_role(conn: Connection, role: rbac_model.Role):
    role.updated_at = datetime.now()
    await rbac_repository.put_role(conn, role)
    return role


async def delete_role(conn: Connection, role_id: UUID):
    await rbac_repository.delete_role(conn, role_id)


async def get_permissions(conn):
    return await rbac_repository.get_permissions(conn)


async def post_user_role(conn, user_role):
    return await rbac_repository.post_user_role(conn, user_role)
