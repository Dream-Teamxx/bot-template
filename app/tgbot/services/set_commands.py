import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from sqlalchemy.orm import sessionmaker

from tgbot.services.repository import Repo

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot, db_pool: sessionmaker):
    commands = [
        BotCommand(
            command="start",
            description="Start",
        ),
    ]

    admin_commands = commands.copy()
    admin_commands.extend([
        BotCommand(
            command="stats",
            description="Статистика",
        ),
        BotCommand(
            command="status",
            description="Статус бота",
        ),
        BotCommand(
            command="maintenance",
            description="Включить режим обслуживания",
        ),
        BotCommand(
            command="stop_maintenance",
            description="Выключить режим обслуживания",
        ),

    ]
    )

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    async with db_pool.begin() as session:
        repo: Repo = Repo(session)
        admins = await repo.get_admins()
    for admin_id in admins:
        logger.info(f'Setting commands for admin {admin_id}')
        await bot.set_my_commands(
            commands=admin_commands,
            scope=BotCommandScopeChat(
                chat_id=admin_id,
            ),
        )
    logger.info('Commands set')
