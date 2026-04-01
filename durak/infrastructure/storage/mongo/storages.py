from copy import deepcopy

from bson import ObjectId
from pymongo import AsyncMongoClient

from durak.infrastructure.storage.protocols import PPersistentStorage


class MongoStorage(PPersistentStorage):
    def __init__(self, client: AsyncMongoClient, database: str, collection: str):
        db = client.get_database(database)
        self.collection = db.get_collection(collection)

    async def get(self, id_: str) -> dict | None:
        query_ = ObjectId(id_) if isinstance(id_, str) else id_
        return await self.collection.find_one(query_)

    async def save(self, value: dict) -> str:
        collection = self.collection
        _id = value.get('_id')
        if _id:
            await collection.replace_one({'_id': ObjectId(_id)}, value, upsert=True)
        else:
            insert = await collection.insert_one(value)
            _id = insert.inserted_id
        return str(_id)

    async def find(
        self,
        query: dict,
        limit: int = 1000,
        offset: int | None = None,
        *,
        timeout_ms: int | None = None,
    ) -> list[dict]:
        cursor = self.collection.find(query).sort('_id', -1)
        if offset is not None:
            cursor = cursor.skip(offset)
        if timeout_ms is not None:
            cursor = cursor.max_time_ms(timeout_ms)
        return await cursor.limit(limit).to_list(length=limit)

    async def count(self, query: dict) -> int:
        return await self.collection.count_documents(query)


class FakeMongoStorage(PPersistentStorage):
    def __init__(self) -> None:
        self.collection: dict[ObjectId, dict] = {}

    async def get(self, id_: str) -> dict | None:
        value = self.collection.get(ObjectId(id_))
        return deepcopy(value) if value is not None else value

    async def find(
        self,
        query: dict,
        limit: int = 1000,
        offset: int | None = None,
    ) -> list[dict]:
        return list(self.collection.values())

    async def count(self, query: dict) -> int:
        return len(self.collection)

    async def save(self, value: dict) -> str:
        _id = value.get('_id')
        if not _id:
            _id = ObjectId()
            value = value | {'_id': _id}
        self.collection[_id] = value
        return str(_id)
