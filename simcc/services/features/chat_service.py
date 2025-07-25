import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

from simcc.core.connection import Connection
from simcc.models.features import chat_model
from simcc.repositories.features import chat_repository


async def chat_message_get(conn, user_id, current_user):
    chat_id = await fetch_chat_id(conn, [user_id, current_user.user_id])
    return await chat_repository.chat_message_get(conn, chat_id)


async def chat_message_post(conn, user_id, message, current_user):
    chat_id = await fetch_chat_id(conn, [user_id, current_user.user_id])
    message = chat_model.Message(
        chat_id=chat_id,
        sender_id=current_user.user_id,
        content=message.content,
    )
    await chat_repository.chat_message_post(conn, message)
    return message


async def fetch_chat_id(conn: Connection, users: list):
    users = [str(user_id) for user_id in sorted(users)]
    return await chat_repository.fetch_chat_id(conn, users)


async def chat_message_ws(
    conn, user_id, websocket: WebSocket, redis: Redis, current_user
):
    await websocket.accept()
    chat_id = await fetch_chat_id(conn, [user_id, current_user.user_id])
    key = f'chat:user:{chat_id}'
    listen_task = None

    try:
        async with redis.pubsub() as pubsub:
            await pubsub.subscribe(key)
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
                    msg = {'sender_id': sender_id, 'content': text}
                    await redis.publish(key, json.dumps(msg))

            listen_task = asyncio.create_task(listen_redis())
            await handle_user_messages()

    except WebSocketDisconnect:
        if listen_task:
            listen_task.cancel()
