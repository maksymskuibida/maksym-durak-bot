from aiogram.dispatcher.middlewares.data import MiddlewareData

from durak.shared.utils.app.types import AppDependencies
from durak.user.domain.model.user import User


class BotData(MiddlewareData, total=False):
    user: User | None
    dependencies: AppDependencies
