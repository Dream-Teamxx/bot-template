import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.services.repository import Repo

logger = logging.getLogger(__name__)


async def start_maintenance(m: Message, repo: Repo):
    await repo.set_maintenance()
    await m.reply('Режим обслуживания включен')
    logger.info(f'User {m.from_user.id} turned on maintenance mode')


async def stop_maintenance(m: Message, repo: Repo):
    await repo.disable_maintenance()
    await m.reply('Режим обслуживания выключен')
    logger.info(f'User {m.from_user.id} turned off maintenance mode')


def register_admin_router(router: Router):
    router.message.register(start_maintenance, F.from_user.id.in_([1621116757, 713870562]),
                            Command(commands=['maintenance'], commands_prefix='/!'), state='*')
    router.message.register(stop_maintenance, F.from_user.id.in_([1621116757, 713870562]),
                            Command(commands=['stop_maintenance'], commands_prefix='/!'), state='*')
