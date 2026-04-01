from typing import Any

from pymongo import AsyncMongoClient

from durak.infrastructure.storage.mongo.storages import MongoStorage
from durak.settings import Settings


def mongo_storage(collection: str):
    def _mongo_storage(dependencies: dict[str, Any]):
        mongo_client: AsyncMongoClient = dependencies['mongo_client']
        settings: Settings = dependencies['settings']
        return MongoStorage(mongo_client, settings.mongo.database, collection)

    return _mongo_storage
