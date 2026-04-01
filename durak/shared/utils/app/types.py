from typing import TypedDict

from pymongo import AsyncMongoClient
from redis.asyncio import Redis

from durak.infrastructure.storage.protocols import PPersistentStorage
from durak.infrastructure.storage.redis import RedisLock
from durak.settings import Settings
from durak.user.infrastructure.storage.protocols import PUserStorage


class AppDependencies(TypedDict, total=False):
    settings: Settings
    mongo_client: AsyncMongoClient
    redis_client: Redis
    lock_factory: RedisLock
    user_mongo_storage: PPersistentStorage
    user_storage: PUserStorage
