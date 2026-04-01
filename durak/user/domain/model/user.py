from enum import StrEnum

from durak.shared.domain.model.base import DataObject, Entity


class TelegramUser(DataObject):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class UserStatus(StrEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class User(Entity):
    status: UserStatus = UserStatus.ACTIVE
    telegram_user: TelegramUser
