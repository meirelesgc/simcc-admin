from datetime import datetime

from simcc.models import researcher_model
from simcc.repositories import researcher_repository


async def researcher_post(conn, researcher):
    ONE = 1
    if not isinstance(researcher, list):
        researcher = [researcher.model_dump()]
    researcher = [researcher_model.ResearcherResponse(**r) for r in researcher]
    await researcher_repository.researcher_post(conn, researcher)
    if len(researcher) == ONE:
        return researcher[0]
    return researcher


async def researcher_get(conn, institution_id, name):
    return await researcher_repository.researcher_get(
        conn, institution_id, name
    )


async def researcher_put(conn, researcher):
    researcher = researcher_model.ResearcherResponse(**researcher.model_dump())
    researcher.updated_at = datetime.now()
    await researcher_repository.researcher_put(conn, researcher)
    return researcher


async def researcher_delete(conn, researcher_id):
    return await researcher_repository.researcher_delete(conn, researcher_id)
