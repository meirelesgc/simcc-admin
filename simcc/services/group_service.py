from datetime import datetime
from uuid import uuid4

from simcc.repositories import group_repository


async def create_group(conn, group):
    group = group.model_dump()
    group['created_at'] = datetime.now()
    group['updated_at'] = datetime.now()
    group['deleted_at'] = None
    group['id'] = uuid4()

    await group_repository.create_group(conn, group)
    return group


async def list_groups(conn, group_id=None):
    return await group_repository.list_groups(conn, group_id)


async def update_group(conn, group_update):
    group_update = group_update.model_dump(exclude_unset=True)
    group_update['updated_at'] = datetime.now()
    await group_repository.update_group(conn, group_update)
    return await group_repository.list_groups(conn, group_update['id'])


async def delete_group(conn, group_id):
    return await group_repository.delete_group(conn, group_id, datetime.now())
