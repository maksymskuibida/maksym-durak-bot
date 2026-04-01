from durak.user.domain.model.user import TelegramUser, User
from durak.user.infrastructure.storage.protocols import PUserStorage


async def create_or_update_user_service(
    telegram_user: TelegramUser, user_storage: PUserStorage
) -> User:
    user = await user_storage.get_by_telegram_id(telegram_user.id)
    if not user:
        user = User(telegram_user=telegram_user)
    else:
        user.telegram_user = telegram_user

    await user_storage.save(user)

    return user
