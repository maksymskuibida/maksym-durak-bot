from typing import AsyncContextManager

from durak.infrastructure.storage.protocols import PEntityPersistentStorage
from durak.user.domain.model.user import User


class PUserStorage(PEntityPersistentStorage[User]):
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    def get_exclusive(
        self,
        booking_id: str,
        timeout: int | None = None,
        blocking_timeout: int | None = None,
    ) -> AsyncContextManager[User]: ...
