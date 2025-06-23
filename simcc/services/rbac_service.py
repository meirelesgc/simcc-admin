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


async def put_role(conn: Connection, role: rbac_model.Role):
    role.updated_at = datetime.now()
    await rbac_repository.put_role(conn, role)
    return role


async def delete_role(conn: Connection, role_id: UUID):
    await rbac_repository.delete_role(conn, role_id)
