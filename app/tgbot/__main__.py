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

from app.tgbot.handlers.setup import register_handlers
from app.tgbot.middlewares.db import DbSessionMiddleware
from app.tgbot.services.set_commands import set_commands
from configreader import config
from tgbot.middlewares.maintenance import MaintenanceMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware

logger = logging.getLogger(__name__)


async def main():
    if config.environment == 'PRODUCTION':

        logging.basicConfig(
            filename='bot_webhook.log',
            filemode='a',
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

    if config.redis_dsn:
        storage = RedisStorage.from_url(config.redis_dsn,
                                        key_builder=DefaultKeyBuilder(prefix='shop_bot', with_destiny=True))
    else:
        storage = MemoryStorage()

    # Creating DB connections pool
    engine = create_async_engine(config.postgres_dsn, future=True)
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    logging.debug('DB successfully initialized')

    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dialog_registry = DialogRegistry(dp)

    # Register middlewares

    dp.callback_query.middleware(DbSessionMiddleware(db_pool))
    dp.inline_query.middleware(DbSessionMiddleware(db_pool))
    dp.message.middleware(MaintenanceMiddleware())
    dp.callback_query.middleware(MaintenanceMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    register_handlers(dp=dp, dialog_registry=dialog_registry)
    try:

        if not config.webhook_domain:

            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            # Suppress aiohttp access log completely
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)
            aiogram_event = logging.getLogger("aiogram.event")
            aiogram_event.setLevel(logging.CRITICAL)

            # Setting webhook
            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )
            # Creating an aiohttp application
            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook_path)
            # API ROUTES if needed
            # app.add_routes([web.get(f'{config.webhook_path}/api', api_handler),
            #                 web.post(f'{config.webhook_path}/api', api_handler)])
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()
            logger.info('Bot started with webhook')

            # Running it forever
            await asyncio.Event().wait()
        await set_commands(bot, db_pool)

    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.info('Bot stopped')
