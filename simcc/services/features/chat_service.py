import asyncio
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

from simcc.core.connection import Connection
from simcc.models.features import chat_model
from simcc.repositories.features import chat_repository


async def chat_message_post(conn, user_id, message, current_user):
    message = chat_model.Message(
        sender_id=current_user.user_id,
        user_id=user_id,
        content=message.content,
    )
    return message
    # await chat_repository.chat_message_post(
    #     conn, user_id, message, current_user
    # )


async def get_chat_id(conn: Connection, users: list):
    users = [str(user_id) for user_id in sorted(users)]
    return await chat_repository.get_chat_id(conn, users)


async def chat_ws(
    conn: Connection,
    chat_id: UUID,
    sender_id: UUID,
    websocket: WebSocket,
    redis: Redis,
):
    await websocket.accept()

    send_channel = f'chat:{chat_id}'

    print(send_channel)

    pubsub = redis.pubsub()
    await pubsub.subscribe(send_channel)

    async def send_to_client():
        async for message in pubsub.listen():
            if message.get('type') == 'message':
                await websocket.send_text(message['data'].decode())

    async def recv_from_client():
        try:
            while True:
                if message := await websocket.receive_text():
                    await chat_repository.post_chat(
                        conn, chat_id, sender_id, message
                    )
                    await redis.publish(send_channel, message)

        except WebSocketDisconnect:
            await pubsub.unsubscribe(send_channel)

    await asyncio.gather(send_to_client(), recv_from_client())
