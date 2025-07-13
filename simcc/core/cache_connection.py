from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool


class CacheConnection:
    def __init__(self, url: str):
        self.pool = ConnectionPool.from_url(url)
        self.client = Redis(connection_pool=self.pool)

    async def connect(self):
        pass

    async def disconnect(self):
        await self.client.close()
