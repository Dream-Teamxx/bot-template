import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from configreader import config
from tgbot.services.repository import Repo
from tgbot.states.main_menu import MainMenu
from tgbot.utils.system_config import getsysteminfo, get_process_uptime


async def configuration(m: Message):
    config = getsysteminfo()
    await m.reply(f'<b>Current server configuration:</b>\n'
                  f'<b>Platform:</b> {config["platform"]}\n'
                  f'<b>Release:</b> {config["platform-release"]}\n'
                  f'<b>Platform version:</b> {config["platform-version"]}\n'
                  f'<b>Architecture:</b> {config["architecture"]}\n'
                  f'<b>Processor:</b> {config["processor"]}\n'
                  f'<b>RAM:</b> {config["ram"]}\n'
                  f'<b>Python version:</b> {config["python"]}\n')


async def status(m: Message):
    service_name = config.service_name
    sysinfo = get_process_uptime(service_name)
    await m.reply(f'<b>Current bot status:</b>\n'
                  f'<b>Status:</b> 🟢 Online\n'
                  f'<b>Uptime:</b> {sysinfo["uptime"]}\n'
                  f'<b>Started at:</b> {sysinfo["since"]}\n')


async def start(m: Message, dialog_manager: DialogManager, repo: Repo, command: CommandObject):
    # if command args needed e.g. /start 123 wil return 123
    # args = command.args
    await repo.update_user_if_not_exists(m.from_user.id, m.from_user.full_name, datetime.datetime.now())
    await dialog_manager.start(MainMenu.main_menu, mode=StartMode.RESET_STACK)


async def get_id(m: Message):
    await m.reply(f'Ваш ID: <code>{m.from_user.id}</code>\n')


def register_user_router(router: Router):
    router.message.register(start, Command(commands='start'), state='*')
    router.message.register(configuration, Command(commands=['config']), state='*')
    router.message.register(status, Command(commands=['status']), state='*')
    router.message.register(get_id, Command(commands=['id']), state='*')
