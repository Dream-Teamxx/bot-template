import typing
from abc import ABC

from aiogram.filters import BaseFilter
from aiogram.types.base import TelegramObject

from tgbot.services.repository import Repo


class AdminFilter(BaseFilter, ABC):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None, **data: typing.Any):
        super().__init__(**data)
        self.is_admin = is_admin

    async def check(self, obj: TelegramObject, repo: Repo):
        if self.is_admin is None or self.is_admin is False:
            return True
        else:
            return obj.from_user.id in await repo.get_admins()
