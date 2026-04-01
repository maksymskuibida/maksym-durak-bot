from contextlib import asynccontextmanager
from typing import Any

from pymongo import AsyncMongoClient

from durak.settings import Settings


@asynccontextmanager
async def mongo_client(dependencies: dict[str, Any]):
    settings: Settings = dependencies['settings']
    client = AsyncMongoClient(settings.mongo.uri)

    try:
        yield client
    finally:
        await client.close()
