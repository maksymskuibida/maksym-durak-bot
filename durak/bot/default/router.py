from aiogram import Router, types
from aiogram.filters import CommandStart

from durak.bot.default.views import StartCommandView
from durak.user.domain.model.user import User

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, user: User):
    view = StartCommandView(user)
    await view.send(message)
