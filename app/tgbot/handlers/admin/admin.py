import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from infrastructure.database.repositories.admin import AdminRepo
from tgbot.services.repository import Repo
from tgbot.states.admin.menu import AdminMenu

logger = logging.getLogger(__name__)


async def admin_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminMenu.admin_menu, mode=StartMode.RESET_STACK)


async def start_maintenance(m: Message, repo: Repo):
    await repo.set_maintenance()
    await m.reply('Режим обслуживания включен')
    logger.info(f'User {m.from_user.id} turned on maintenance mode')


async def stop_maintenance(m: Message, repo: Repo):
    await repo.disable_maintenance()
    await m.reply('Режим обслуживания выключен')
    logger.info(f'User {m.from_user.id} turned off maintenance mode')


async def add_admin(m: Message, command: CommandObject, admin_repo: AdminRepo):
    new_admin = command.args
    try:
        admin_id = int(new_admin)
    except TypeError:
        await m.reply('Please specify admin id')
        return
    except ValueError:
        await m.reply('Admin id must be integer')
        return
    result = await admin_repo.add_admin(admin_id)
    if result:
        logger.info(f'User {m.from_user.id} added admin {admin_id}')
        await m.reply(f'Пользователь {admin_id} добавлен в список админов')
    else:
        await m.reply(f'Пользователь {admin_id} не найден')
        logger.info(f'User {m.from_user.id} tried to add admin {admin_id}, but he is not found')


async def ban_user(m: Message, command: CommandObject, admin_repo: AdminRepo):
    user_id = command.args
    try:
        user_id = int(user_id)
    except TypeError:
        await m.reply('Please specify user id')
        return
    except ValueError:
        await m.reply('User id must be integer')
        return
    result = await admin_repo.ban_user(user_id)
    if result:
        logger.info(f'User {m.from_user.id} banned {user_id}')
        await m.reply(f'Пользователь {user_id} заблокирован')
    else:
        await m.reply(f'Пользователь {user_id} не найден')
        logger.info(f'User {m.from_user.id} tried to ban {user_id}, but he is not found')


def register_admin_router(router: Router):
    router.message.register(start_maintenance,
                            Command(commands=['maintenance'], commands_prefix='/!'), state='*')
    router.message.register(stop_maintenance,
                            Command(commands=['stop_maintenance'], commands_prefix='/!'), state='*')
    router.message.register(add_admin,
                            Command(commands=['add_admin'], commands_prefix='/!'), state='*')
    router.message.register(ban_user,
                            Command(commands=['ban'], commands_prefix='/!'), state='*')
