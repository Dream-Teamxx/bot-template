from aiogram import Dispatcher, Router, F
from aiogram_dialog import DialogRegistry

from tgbot.handlers.admin.admin import register_admin_router
from tgbot.handlers.user.start import register_user_start_router


def register_handlers(dp: Dispatcher, dialog_registry: DialogRegistry):
    user_router = Router()
    admin_router = Router()
    dialogs_router = Router()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    register_admin_router(admin_router)
    register_user_start_router(user_router)
    dialogs_router.message.filter(F.chat.type == "private")
    user_router.include_router(dialogs_router)
