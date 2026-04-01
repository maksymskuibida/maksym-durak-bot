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

    @property
    def tg_chat_id(self):
        return self.telegram_user.id

    @property
    def first_name(self) -> str:
        return self.telegram_user.first_name

    @property
    def last_name(self) -> str | None:
        return self.telegram_user.last_name

    @property
    def name(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    @property
    def tg_username(self):
        return self.telegram_user.username

    @property
    def tg_mention(self) -> str | None:
        if not (username := self.tg_username):
            return '@' + username
        return None
