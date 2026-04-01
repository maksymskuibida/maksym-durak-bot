from typing import Any, Awaitable, Callable, TypeAlias

from aiogram import types

from durak.bot.types import BotData
from durak.shared.application.services import inject_dependencies
from durak.user.application.services import create_or_update_user_service

SupportedEvent: TypeAlias = types.Message | types.CallbackQuery


async def user_middleware(
    handler: Callable[[SupportedEvent, BotData], Awaitable[Any]],
    event: SupportedEvent,
    data: BotData,
):
    service = inject_dependencies(create_or_update_user_service, data)
    user = await service(event.from_user)
    data['user'] = user

    return await handler(event, data)
