from aiogram import Router

from durak.bot.router import default
from durak.user.application.middlewares import user_middleware

router = Router()

router.message.outer_middleware(user_middleware)
router.callback_query.outer_middleware(user_middleware)


router.include_router(default.router)
