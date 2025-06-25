from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import researcher_model
from simcc.services import researcher_service

router = APIRouter()


ALLOWED = ['ADMIN', 'RESEARCHER']


@router.post(
    '/researcher/',
    status_code=HTTPStatus.CREATED,
    response_model=researcher_model.ResearcherResponse | list,
)
async def researcher_post(
    researcher: researcher_model.CreateResearcher,
    conn: Connection = Depends(get_conn),
):
    return await researcher_service.researcher_post(conn, researcher)


@router.get(
    '/researcher/',
    response_model=list[researcher_model.ResearcherResponse],
)
async def researcher_get(
    institution_id: UUID = None,
    name: str = None,
    conn: Connection = Depends(get_conn),
):
    return await researcher_service.researcher_get(conn, institution_id, name)


@router.put(
    '/researcher/',
    response_model=researcher_model.ResearcherResponse,
)
async def researcher_put(
    researcher: researcher_model.UpdateResearcher,
    conn: Connection = Depends(get_conn),
):
    return await researcher_service.researcher_put(conn, researcher)


@router.delete(
    '/researcher/{researcher_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def researcher_delete(
    researcher_id: UUID,
    conn: Connection = Depends(get_conn),
):
    return await researcher_service.researcher_delete(conn, researcher_id)
