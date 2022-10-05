import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram_dialog import DialogRegistry
from aiohttp import web

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from app.config import load_config
from app.tgbot.handlers.setup import register_handlers
from app.tgbot.middlewares.db import DbSessionMiddleware
from app.tgbot.services.set_commands import set_commands

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        # filename='bot_webhook.log',
        # filemode='a',
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.error('Starting bot')
    config = load_config()

    if config.tg_bot.use_redis:
        storage = RedisStorage.from_url(
            url=f'redis://{config.redis.host}', connection_kwargs={
                'db': config.redis.db,
            },
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )
    else:
        storage = MemoryStorage()

    # Creating DB connections pool
    logging.debug('DB successfully initialized')
    engine = create_async_engine(config.db.postgres_dsn, future=True)
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dialog_registry = DialogRegistry(dp)

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))

    register_handlers(dp=dp, dialog_registry=dialog_registry)
    try:

        if not config.tg_bot.use_webhook:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            # Suppress aiohttp access log completely
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            # Setting webhook
            await bot.set_webhook(
                url=config.tg_bot.webhook_host + config.tg_bot.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            # Creating an aiohttp application
            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.tg_bot.webhook_path)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.tg_bot.app_host, port=config.tg_bot.app_port)
            await site.start()

            # Running it forever
            await asyncio.Event().wait()
        await set_commands(bot, config)

    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.info('Bot stopped')
