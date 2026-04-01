from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable

from funcy import compact

from durak.infrastructure.storage.entity import EntityPersistentStorage
from durak.infrastructure.storage.protocols import PLock, PPersistentStorage
from durak.infrastructure.storage.serializers import MongoSerializer
from durak.user.domain.model.user import User
from durak.user.infrastructure.storage.protocols import PUserStorage


class UserStorage(PUserStorage):
    def __init__(
        self,
        storage: PPersistentStorage,
        lock_factory: Callable[..., PLock],
    ):
        self._lock_factory = lock_factory
        self._storage = EntityPersistentStorage[User](
            storage=storage,
            serializer=MongoSerializer(User),
        )

    async def get(self, id_: str) -> User | None:
        return await self._storage.get(id_)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        users = await self._storage.find({'telegram_user.id': telegram_id})
        if users:
            return users[0]
        return None

    def _lock_name(self, user_id: str) -> str:
        return f'user:lock:{user_id}'

    @asynccontextmanager
    async def get_exclusive(
        self,
        booking_id: str,
        timeout: int | None = None,
        blocking_timeout: int | None = None,
    ) -> AsyncIterator[User]:
        params = {
            'blocking_timeout': blocking_timeout,
            'name': self._lock_name(booking_id),
            'timeout': timeout,
        }
        async with self._lock_factory(**compact(params)):
            yield await self.get(booking_id)

    async def save(self, user: User) -> str:
        assert user
        return await self._storage.save(user)

    @classmethod
    def dependency(cls, dependencies: dict[str, Any]):
        user_mongo_storage: PPersistentStorage = dependencies['user_mongo_storage']
        return cls(user_mongo_storage, dependencies['lock_factory'])
