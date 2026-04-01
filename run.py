import asyncio

from durak.bot.app import run_app


async def main():
    await run_app()


if __name__ == '__main__':
    asyncio.run(main())
