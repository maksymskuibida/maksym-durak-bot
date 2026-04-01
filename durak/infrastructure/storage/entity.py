from durak.infrastructure.storage.protocols import (
    PEntityPersistentStorage,
    PEntitySerializer,
    PPersistentStorage,
)


class EntityPersistentStorage[T](PEntityPersistentStorage):
    def __init__(
        self,
        storage: PPersistentStorage,
        serializer: PEntitySerializer[T, dict],
    ):
        self.storage = storage
        self._serializer = serializer

    async def get(self, key: str) -> T | None:
        stored = await self.storage.get(key)
        return self._transform(stored) if stored else stored

    async def find(self, query: dict) -> list[T]:
        stored = await self.storage.find(query)
        return [*map(self._transform, stored)]

    def _transform(self, stored: dict) -> T:
        return self._serializer.to_internal_value(stored)

    async def save(self, entity: T) -> str:
        payload = self._serializer.to_representation(entity)
        id_ = await self.storage.save(payload)
        entity_id = str(id_)
        if hasattr(entity, 'id_') and entity.id_ is None:
            entity.id_ = entity_id
        return entity_id
