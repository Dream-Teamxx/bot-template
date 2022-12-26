from typing import List

from pydantic import parse_obj_as
from sqlalchemy import select, update

from domain.dto.user import UserDTO
from infrastructure.database.models.user import User
from infrastructure.database.repositories.repo import SQLAlchemyRepo


class AdminRepo(SQLAlchemyRepo):
    async def get_admins(self):
        query = select(User).where(User.is_admin == True)
        _ = await self.session.execute(query)
        return parse_obj_as(List[UserDTO], _.scalars().all())

    async def add_admin(self, admin_id: int):
        query = update(User).where(User.user_id == admin_id).values(
            is_admin=True)
        _ = await self.session.execute(query)
        await self.session.commit()
        return _.rowcount

    async def remove_admin(self, admin_id: int):
        query = update(User).where(User.user_id == admin_id).values(
            is_admin=False)
        _ = await self.session.execute(query)
        await self.session.commit()
        return _.rowcount

    async def ban_user(self, user_id: int):
        query = update(User).where(User.user_id == user_id).values(
            is_blocked=True, is_admin=False, is_trader=False)
        _ = await self.session.execute(query)
        await self.session.commit()
        return _.rowcount
