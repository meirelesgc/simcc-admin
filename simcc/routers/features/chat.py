from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from redis.asyncio.client import Redis

from simcc.core.connection import Connection
from simcc.core.database import get_cache_conn, get_conn
from simcc.schemas import user_model
from simcc.schemas.features import chat_schema
from simcc.security import get_current_user
from simcc.services.features import chat_service

router = APIRouter()

Conn = Annotated[Connection, Depends(get_conn)]
Cache = Annotated[Redis, Depends(get_cache_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]


@router.post(
    '/chat/',
    # response_class=chat_schema.ChatPubic,
    status_code=HTTPStatus.CREATED,
)
async def create_chat(
    conn: Conn,
    current_user: CurrentUser,
    chat: chat_schema.ChatSchema,
):
    return await chat_service.create_private_chat(conn, current_user, chat)


@router.websocket('/ws/chat/{chat_id}')
async def link(
    conn: Conn,
    redis: Cache,
    chat_id: UUID,
    websocket: WebSocket,
    current_user: CurrentUser,
):
    await chat_service.link(conn, current_user, chat_id, websocket, redis)
