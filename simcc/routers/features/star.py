# simcc/routers/star_router.py

from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.models import user_model
from simcc.models.features import star_models
from simcc.security import get_current_user
from simcc.services.features import star_service

router = APIRouter()


@router.post(
    '/stars/',
    tags=['Stars'],
    status_code=HTTPStatus.CREATED,
    response_model=star_models.Star,
)
async def post_star(
    star: star_models.CreateStar,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await star_service.post_star(conn, star, current_user)


@router.get(
    '/stars/',
    tags=['Stars'],
    response_model=list[star_models.Star],
)
async def get_stars(
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await star_service.get_stars(conn, current_user)


@router.delete(
    '/stars/{entry_id}/',
    tags=['Stars'],
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_star(
    entry_id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    success = await star_service.delete_star(conn, entry_id, current_user)
    if not success:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Star not found for this user and entry_id',
        )
