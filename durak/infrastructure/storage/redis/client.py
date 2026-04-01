from contextlib import asynccontextmanager
from typing import Any

from redis.asyncio import Redis

from durak.settings import Settings


@asynccontextmanager
async def redis_client(dependencies: dict[str, Any]):
    settings: Settings = dependencies['settings']
    client = Redis.from_url(settings.redis.uri)

    try:
        yield client
    finally:
        await client.close()
