import asyncio
import json
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
from redis.asyncio.client import Redis

from simcc.core.connection import Connection
from simcc.repositories.features import chat_repository
from simcc.schemas import user_model
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
        chat = chat_schema.Chat(
            **chat.model_dump(), chat_id=chat_id.get('chat_id')
        )
        return chat

    if not chat.chat_name:
        chat.chat_name = ' & '.join(chat.users)

    chat = chat_schema.Chat(**chat.model_dump())

    await chat_repository.create_chat_record(conn, chat)
    await chat_repository.add_chat_participants(conn, chat)
    return chat


async def link(
    conn: Connection,
    current_user: user_model.User,
    chat_id: UUID,
    websocket: WebSocket,
    redis: Redis,
):
    await websocket.accept()

    link_is_valid = await chat_repository.validate_link(
        conn, current_user, chat_id
    )
    if not link_is_valid:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason='Permission denied'
        )
        return

    listen_task = None
    handle_task = None

    channel_name = f'chat:{chat_id}'

    try:
        async with redis.pubsub() as pubsub:
            await pubsub.subscribe(channel_name)
            await websocket.send_text(json.dumps({'status': 'connected'}))

            async def listen_redis():
                async for message in pubsub.listen():
                    if message['type'] != 'message':
                        continue
                    data = message['data']
                    if isinstance(data, bytes):
                        data = data.decode()
                    await websocket.send_text(data)

            async def handle_user_messages():
                while True:
                    text = await websocket.receive_text()
                    sender_id = str(current_user.user_id)

                    msg = chat_schema.Message(
                        chat_id=chat_id, sender_id=sender_id, content=text
                    )

                    await chat_repository.save_message(conn, msg)

                    msg = msg.model_dump(mode='json')

                    await redis.publish(channel_name, json.dumps(msg))

            listen_task = asyncio.create_task(listen_redis())
            handle_task = asyncio.create_task(handle_user_messages())

            await asyncio.gather(listen_task, handle_task)

    except WebSocketDisconnect:
        print(f'Client disconnected from chat {chat_id}')

    finally:
        if listen_task and not listen_task.done():
            listen_task.cancel()
        if handle_task and not handle_task.done():
            handle_task.cancel()


async def get_chats(conn, current_user):
    return await chat_repository.get_chats(conn, current_user)
