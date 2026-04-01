from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from durak.bot.router import router

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(router)
