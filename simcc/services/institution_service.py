from datetime import datetime

from simcc.core.connection import Connection
from simcc.models import institution_model
from simcc.repositories import institution_repository


async def post_institution(institution, conn: Connection):
    ONE = 1
    if not isinstance(institution, list):
        institution = [institution.model_dump()]
    institution = [institution_model.Institution(**i) for i in institution]
    await institution_repository.post_institution(institution, conn)
    if len(institution) == ONE:
        return institution[0]
    return institution


async def get_institution(conn: Connection, institution_id):
    return await institution_repository.get_institution(institution_id, conn)


async def put_institution(
    conn: Connection, institution: institution_model.Institution
):
    institution.updated_at = datetime.now()
    await institution_repository.put_institution(institution, conn)
    return institution


async def delete_institution(conn: Connection, institution_id):
    return await institution_repository.delete_institution(
        institution_id, conn
    )
