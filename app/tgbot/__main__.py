import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
# from app.tgbot.db.models import create_tables
from app.tgbot.dialogs.misc.inline_search import inline_router
from app.tgbot.dialogs.misc.setup import setup_dialogs
from app.tgbot.dialogs.user.user_main import register_handlers_user
from magic_filter import F
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app import config
from app.tgbot.middlewares.db import DbSessionMiddleware


async def main():
    # Logging config
    logging.basicConfig(
        # filename='bot_webhook.log',
        # filemode='a',
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info('Starting bot')

    # Creating DB engine for PostgreSQL
    engine = create_async_engine(config.db.postgres_dsn, future=True)

    # Creating DB connections pool
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    logging.debug('DB successfully initialized')

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token, parse_mode="HTML")

    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(config.custom_bot_api, is_local=True)

    # Choosing FSM storage
    if config.bot_fsm_storage == "memory":
        dp = Dispatcher(storage=MemoryStorage())
    else:
        dp = Dispatcher(storage=RedisStorage.from_url(config.redis_dsn))

    # Allow interaction in private chats (not groups or channels) only
    dp.message.filter(F.chat.type == "private")

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))

    # Routers
    main_router = Router()
    user_router = Router()
    admin_router = Router()

    # Register routers
    dp.include_router(main_router)
    main_router.include_router(user_router)
    main_router.include_router(admin_router)
    main_router.include_router(inline_router)

    # Register handlers
    register_handlers_user(user_router)
    setup_dialogs(dp)

    try:

        if not config.webhook_domain:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            # Suppress aiohttp access log completely
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            # Setting webhook
            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            # Creating an aiohttp application
            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook_path)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()

            # Running it forever
            await asyncio.Event().wait()

    finally:
        await bot.session.close()


asyncio.run(main())