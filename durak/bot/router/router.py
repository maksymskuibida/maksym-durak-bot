from aiogram import Router

from durak.bot.router import default

router = Router()

router.include_router(default.router)
