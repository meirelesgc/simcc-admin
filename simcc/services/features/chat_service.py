from http import HTTPStatus

from fastapi import HTTPException

from simcc.repositories.features import chat_repository
from simcc.schemas.features import chat_schema
from simcc.schemas.user_model import User


async def create_private_chat(
    conn,
    current_user: User,
    chat: chat_schema.ChatSchema,
):
    if current_user.user_id not in chat.users:
        HTTPException(status_code=HTTPStatus.FORBIDDEN)

    if chat_id := await chat_repository.get_private_chat(conn, chat):
        chat = chat_schema.Chat(**chat.model_dump(), chat_id=chat_id)
        return chat

    if not chat.chat_name:
        chat.chat_name = ' & '.join(chat.users)

    chat = chat_schema.Chat(**chat.model_dump())

    await chat_repository.create_chat_record(conn, chat)
    await chat_repository.add_chat_participants(conn, chat)
    return chat


async def link(conn, current_user, chat_id, websocket, redis): ...
