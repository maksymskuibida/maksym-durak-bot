from functools import partial
from types import TracebackType
from typing import Any, Self

from redis.asyncio import Redis

from durak.infrastructure.storage.protocols import PLock
from durak.infrastructure.storage.redis.constants import DEFAULT_REDIS_LOCK_TIMEOUT
from durak.settings import Settings


class RedisLock(PLock):
    def __init__(
        self,
        client: Redis,
        name: str,
        timeout: int | None = DEFAULT_REDIS_LOCK_TIMEOUT,
        blocking_timeout: int | None = DEFAULT_REDIS_LOCK_TIMEOUT,
    ):
        self.name = name
        self.timeout = timeout
        self.blocking_timeout = blocking_timeout
        self.lock = client.lock(
            name=name, timeout=timeout, blocking_timeout=blocking_timeout
        )

    async def __aenter__(self) -> Self:
        await self.lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.lock.release()

    async def is_locked(self) -> bool:
        return await self.lock.locked()

    @staticmethod
    def create_fake(name: str, timeout: int | None = None) -> PLock:
        return FakeRedisLock(name=name, timeout=timeout)

    @classmethod
    def factory_dependency(cls, dependencies: dict[str, Any]):
        settings: Settings = dependencies['settings']
        return partial(
            cls,
            client=dependencies['redis_client'],
            timeout=settings.redis.timeout,
            blocking_timeout=settings.redis.timeout,
        )


class FakeRedisLock(PLock):
    def __init__(
        self, name: str, timeout: int | None = None, blocking_timeout: int | None = None
    ):
        self.name = name
        self.timeout = timeout
        self.blocking_timeout = blocking_timeout
        self._locked = False

    async def __aenter__(self) -> Self:
        assert not self._locked, f'Lock {self.name!r} is already locked'
        self._locked = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        assert self._locked, f'Lock {self.name} is not locked'
        self._locked = False

    async def is_locked(self) -> bool:
        return self._locked
