from aiogram import Dispatcher, Router
from aiogram_dialog import DialogRegistry

from tgbot.filters.role import AdminFilter
from tgbot.handlers.user.user import register_start


def register_handlers(dp: Dispatcher, dialog_registry: DialogRegistry):
    register_start(dp)

    admin_router = Router()
    dp.include_router(admin_router)
    admin_router.message.filter(AdminFilter())
