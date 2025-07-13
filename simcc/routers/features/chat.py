import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

from simcc.core.database import get_cache_conn

router = APIRouter()


@router.websocket('/ws/{room_id}')
async def websocket_endpoint(
    room_id: str,
    websocket: WebSocket,
    redis: Redis = Depends(get_cache_conn),
):
    await websocket.accept()
    pubsub = redis.pubsub()
    channel = f'chat:{room_id}'
    await pubsub.subscribe(channel)

    async def send_to_client():
        async for message in pubsub.listen():
            if message.get('type') == 'message':
                await websocket.send_text(message['data'].decode())

    async def recv_from_client():
        try:
            while True:
                text = await websocket.receive_text()
                await redis.publish(channel, text)
        except WebSocketDisconnect:
            await pubsub.unsubscribe(channel)

    await asyncio.gather(send_to_client(), recv_from_client())
