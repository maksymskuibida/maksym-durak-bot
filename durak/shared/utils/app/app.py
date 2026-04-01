from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, AsyncContextManager, Awaitable, Callable, TypeAlias

from aiogram import Bot, Dispatcher

from durak.shared.utils.app.types import AppDependencies

Dependency: TypeAlias = (
    Callable[[dict[str, Any]], AsyncContextManager[Any, Any]]
    | Callable[[dict[str, Any]], Awaitable[Any]]
    | Callable[[dict[str, Any]], Any]
)


class AppAsyncExitStack(AsyncExitStack):
    pass


class App:
    def __init__(self, dp: Dispatcher, *bots: Bot | Callable[[AppDependencies], Bot]):
        self.dp = dp
        self._bots = bots
        self.dependency_definitions: dict[str, Dependency] = {}
        self.dependencies: dict[str, Any] = {}

    def add_dependency(self, name: str, dependency: Dependency):
        if name in self.dependency_definitions:
            raise ValueError(f"Dependency with name {name} already exists")
        self.dependency_definitions[name] = dependency

    def get_bots(self):
        return (
            (
                bot
                if isinstance(bot, Bot)
                else bot(AppDependencies(**self.dp.workflow_data))
            )
            for bot in self._bots
        )

    @asynccontextmanager
    async def init(self, dependencies_override: dict[str, Dependency] | None = None):
        if not dependencies_override:
            dependencies_override = {}
        async with AsyncExitStack() as stack:
            dependencies: dict[str, Any] = {}

            for name, dependency_func in self.dependency_definitions.items():
                dependency_func = dependencies_override.get(name, dependency_func)

                result = dependency_func(dependencies)

                if hasattr(result, "__aenter__"):
                    dependency = await stack.enter_async_context(result)
                elif asyncio.iscoroutine(result):
                    dependency = await result
                else:
                    dependency = result

                dependencies[name] = dependency

            self.dp.workflow_data.update(dependencies)
            yield

    async def run(self):
        await self.dp.start_polling(*tuple(self.get_bots()))
