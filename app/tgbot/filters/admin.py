from aiogram.filters import BaseFilter
from aiogram.types import Message

from infrastructure.database.repositories.user import UserReader


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, user_reader: UserReader):
        admins = await user_reader.get_admins()
        admins = [admin.user_id for admin in admins]
        return message.from_user.id in admins
