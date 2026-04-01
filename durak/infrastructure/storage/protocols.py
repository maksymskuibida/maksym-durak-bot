from abc import abstractmethod
from typing import Any, AsyncContextManager, Protocol


class PLock(AsyncContextManager, Protocol):
    name: str
    timeout: int | None
    blocking_timeout: int | None

    @abstractmethod
    async def is_locked(self) -> bool:
        raise NotImplementedError


class PPersistentStorage(Protocol):
    async def get(self, id_: str) -> Any: ...

    async def save(self, value: Any) -> str: ...

    async def find(
        self,
        query: dict,
        limit: int = 1000,
        offset: int | None = None,
    ) -> Any: ...

    async def count(self, query: dict) -> int: ...


class PEntityPersistentStorage[T](Protocol):
    async def get(self, id_: str) -> T | None: ...

    async def save(self, value: T) -> str: ...

    async def find(self, query: dict) -> list[T]: ...


class PEntitySerializer[T, R](Protocol):
    def to_representation(self, entity: T) -> R: ...

    def to_internal_value(self, payload: R) -> T: ...
