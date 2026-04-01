from typing import Any, Awaitable, Callable

from aiogram import types

from durak.bot.middlewares.helpers import inject_dependencies
from durak.bot.types import BotData
from durak.user.application.services.create_or_update import (
    create_or_update_user_service,
)
from durak.user.domain.model.user import TelegramUser


async def _user_middleware(
    event: types.Update,
    data: BotData,
):
    event_item = getattr(event, event.event_type)
    if not hasattr(event_item, 'from_user'):
        return

    from_user: types.User = event_item.from_user
    telegram_user = TelegramUser(**from_user.model_dump())

    service = inject_dependencies(create_or_update_user_service, data)
    user = await service(telegram_user)
    data['user'] = user


async def user_middleware(
    handler: Callable[[types.Update, BotData], Awaitable[Any]],
    event: types.Update,
    data: BotData,
):
    await _user_middleware(event, data)
    return await handler(event, data)
