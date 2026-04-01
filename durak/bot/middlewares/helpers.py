import inspect
from functools import partial
from typing import Callable

from durak.bot.types import BotData


def inject_dependencies(func: Callable, data: BotData) -> Callable:
    params = inspect.signature(func).parameters
    deps = {name: dep for name, dep in data.items() if name in params}
    return partial(func, **deps)
