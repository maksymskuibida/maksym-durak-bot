from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from durak.bot import default
from durak.bot.middlewares.user import user_middleware

dp = Dispatcher(storage=MemoryStorage())

dp.update.outer_middleware(user_middleware)

dp.include_router(default.router)
