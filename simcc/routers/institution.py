from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import institution_model, user_model
from simcc.security import get_current_user
from simcc.services import institution_service

router = APIRouter()


@router.post(
    '/InstitutionRest/Insert',
    deprecated=True,
)
@router.post(
    '/institution/',
    response_model=institution_model.Institution | list,
    status_code=HTTPStatus.CREATED,
)
async def post_institution(
    institution: institution_model.CreateInstitution | list = Body(...),
    conn: Connection = Depends(get_conn),
    current_user: user_model.UserResponse = Depends(get_current_user),
):
    return await institution_service.post_institution(institution, conn)


@router.put(
    '/Query/Count',
    deprecated=True,
)
@router.get(
    '/institution/{institution_id}/',
    response_model=institution_model.InstitutionStats,
)
async def get_institution(
    institution_id: UUID,
    conn: Connection = Depends(get_conn),
):
    institution = await institution_service.get_institution(
        conn, institution_id
    )
    if institution is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Institution with ID {institution_id} not found.',
        )
    return institution


@router.put(
    '/InstitutionRest/Update',
    deprecated=True,
)
@router.put(
    '/institution/',
    response_model=institution_model.Institution,
)
async def put_institution(
    institution: institution_model.Institution,
    conn: Connection = Depends(get_conn),
    current_user: user_model.UserResponse = Depends(get_current_user),
):
    institution = await institution_service.put_institution(conn, institution)
    return institution


@router.post(
    '/InstitutionRest/Delete',
    deprecated=True,
)
@router.delete(
    '/institution/{institution_id}/',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_institution(
    institution_id: UUID,
    conn: Connection = Depends(get_conn),
    current_user: user_model.UserResponse = Depends(get_current_user),
):
    await institution_service.delete_institution(conn, institution_id)
