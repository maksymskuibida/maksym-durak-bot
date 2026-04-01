from contextlib import asynccontextmanager
from typing import Callable

from aiogram import Bot, Dispatcher

from durak.bot.bot import get_bot
from durak.bot.dispatcher import dp
from durak.infrastructure.storage.mongo.client import mongo_client
from durak.infrastructure.storage.mongo.dependency import mongo_storage
from durak.infrastructure.storage.redis import RedisLock
from durak.infrastructure.storage.redis.client import redis_client
from durak.settings.dependency import settings_dependency
from durak.shared.utils.app.app import App, Dependency
from durak.user.infrastructure.storage.storage import UserStorage


def add_dependencies(app: App):
    app.add_dependency('settings', settings_dependency)
    app.add_dependency('mongo_client', mongo_client)
    app.add_dependency('redis_client', redis_client)
    app.add_dependency('lock_factory', RedisLock.factory_dependency)
    app.add_dependency('user_mongo_storage', mongo_storage('users'))
    app.add_dependency('user_storage', UserStorage.dependency)


@asynccontextmanager
async def init_app(
    _dp: Dispatcher = dp,
    bots: tuple[Bot | Callable[[], Bot]] = (get_bot,),
    dependencies_override: dict[str, Dependency] | None = None,
):
    app = App(_dp, *bots)
    add_dependencies(app)
    async with app.init(dependencies_override):
        yield app


async def run_app(
    _dp: Dispatcher = dp, dependencies_override: dict[str, Dependency] | None = None
):
    async with init_app(_dp, dependencies_override=dependencies_override) as app:
        await app.run()
