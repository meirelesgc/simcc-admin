from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket
from redis.asyncio.client import Redis

from simcc.core.connection import Connection
from simcc.core.database import get_cache_conn, get_conn
from simcc.models import user_model
from simcc.models.features import chat_model
from simcc.security import get_current_user
from simcc.services.features import chat_service

router = APIRouter()


@router.post(
    '/chat/user/{user_id}/',
    status_code=HTTPStatus.CREATED,
    response_model=chat_model.Message,
)
async def chat_message_post(
    user_id: UUID,
    message: chat_model.CreateMessage,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await chat_service.chat_message_post(
        conn, user_id, message, current_user
    )


@router.get(
    '/chat/user/{user_id}/',
    response_model=list[chat_model.Message],
)
async def chat_message_get(
    user_id: UUID,
    current_user: user_model.User = Depends(get_current_user),
    conn: Connection = Depends(get_conn),
):
    return await chat_service.chat_message_get(conn, user_id, current_user)


@router.websocket('/ws/chat/user/{user_id}/')
async def chat_message_ws(
    user_id: UUID,
    websocket: WebSocket,
    token: str = Query(),
    redis: Redis = Depends(get_cache_conn),
    conn: Connection = Depends(get_conn),
):
    current_user: user_model.User = await get_current_user(token, conn)
    await chat_service.chat_message_ws(
        conn, user_id, websocket, redis, current_user
    )
