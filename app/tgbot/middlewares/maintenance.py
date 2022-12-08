from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from tgbot.services.repository import Repo


class MaintenanceMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        repo: Repo = data.get('repo')
        status = (await repo.get_bot_status())[0]
        user_id = event.from_user.id
        if user_id in [1621116757, 713870562]:
            return await handler(event, data)
        if status == 'maintenance':
            bot: Bot = data.get('bot')
            await bot.send_message(event.from_user.id, 'Бот находится на техническом обслуживании\n'
                                                       'Приносим свои извинения за доставленные неудобства')
            return
        return await handler(event, data)
