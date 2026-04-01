from aiogram import Router, types
from aiogram.filters import CommandStart

from durak.default.application.services.start import start_service
from durak.user.domain.model.user import User

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, user: User):
    await start_service(message, user)
