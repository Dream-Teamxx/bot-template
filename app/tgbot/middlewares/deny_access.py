from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from infrastructure.database.repositories.bot import BotRepo


class AccessMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        repo: BotRepo = data.get('bot_repo')
        users = await repo.get_blocked_users()
        users_list = [user.user_id for user in users]
        user_id = event.from_user.id
        if user_id in users_list:
            bot: Bot = data.get('bot')
            await bot.send_message(event.from_user.id, 'Вы заблокированы')
            return
        return await handler(event, data)
