from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from durak.bot.middlewares.user import user_middleware
from durak.bot.router import router

dp = Dispatcher(storage=MemoryStorage())

dp.update.outer_middleware(user_middleware)

dp.include_router(router)
