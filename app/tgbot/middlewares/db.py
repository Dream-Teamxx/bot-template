from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker

from infrastructure.database.repositories.admin import AdminRepo
from infrastructure.database.repositories.bot import BotRepo
from infrastructure.database.repositories.invoice import InvoiceRepo
from infrastructure.database.repositories.item import UserItemReader, UserItemRepo, TraderItemReader, TraderItemRepo
from infrastructure.database.repositories.repo import SQLAlchemyRepo
from infrastructure.database.repositories.user import UserRepo, UserReader


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, sm: sessionmaker):
        super().__init__()
        self.Session = sm

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.Session() as session:
            data["session"] = session
            data['admin_repo'] = AdminRepo(session)
            data["main_repo"] = SQLAlchemyRepo(session)
            data["bot_repo"] = BotRepo(session)
            data["user_reader"] = UserReader(session)
            data["user_repo"] = UserRepo(session)
            data["user_item_reader"] = UserItemReader(session)
            data["user_item_repo"] = UserItemRepo(session)
            data["trader_item_reader"] = TraderItemReader(session)
            data["trader_item_repo"] = TraderItemRepo(session)
            data['invoice_repo'] = InvoiceRepo(session)
            return await handler(event, data)
