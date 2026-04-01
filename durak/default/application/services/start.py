from aiogram import types

from durak.user.domain.model.user import User


async def start_service(message: types.Message, user: User):
    await message.answer(f"HI, {user.telegram_user.first_name} {user.id_}")
