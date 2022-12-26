from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from infrastructure.database.repositories.bot import BotRepo


class MaintenanceMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        repo: BotRepo = data.get('bot_repo')
        bot_settings = await repo.get_bot_settings()
        user_id = event.from_user.id
        if user_id in [713870562]:
            return await handler(event, data)
        if bot_settings.status == 'maintenance':
            bot: Bot = data.get('bot')
            await bot.send_message(event.from_user.id, 'Бот находится на техническом обслуживании\n'
                                                       'Приносим свои извинения за доставленные неудобства')
            return
        elif bot_settings.status is None:
            bot: Bot = data.get('bot')
            alert_group = bot_settings.alert_group
            await bot.send_message(alert_group, 'Необходимо установить статус бота')
            return
        return await handler(event, data)
