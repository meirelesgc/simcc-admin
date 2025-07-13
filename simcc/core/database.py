from simcc.config import Settings
from simcc.core.cache_connection import CacheConnection
from simcc.core.connection import Connection

conn = Connection(
    Settings().get_connection_string(),
    max_size=20,
    timeout=10,
)

cache_conn = CacheConnection(
    url=Settings().REDIS,
)


async def get_cache_conn():
    return cache_conn.client


async def get_conn():
    yield conn
