from aiogram import Bot

from durak.shared.utils.app.types import AppDependencies


def get_bot(dependencies: AppDependencies) -> Bot:
    return Bot(dependencies['settings'].bot.token)
