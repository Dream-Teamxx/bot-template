from datetime import datetime

from pydantic import parse_obj_as
from sqlalchemy import select, insert
from sqlalchemy import update

from domain.dto.user import UserDTO
from infrastructure.database.models.user import User
from infrastructure.database.repositories.repo import SQLAlchemyRepo


class UserRepo(SQLAlchemyRepo):
    async def update_user_if_not_exists(self, user_id: int, full_name: str, registered_at: datetime):
        sql = select(User.user_id).where(User.user_id == user_id)
        result = (await self.session.execute(sql)).first()
        if not result:
            await self.session.execute(
                insert(User).values(user_id=user_id, full_name=full_name, registered_at=registered_at))
            await self.session.commit()

    async def update_balance(self, user_id: int, amount: float):
        await self.session.execute(
            update(User).values(balance=User.balance + amount).where(
                User.user_id == user_id))
        await self.session.commit()


class UserReader(SQLAlchemyRepo):
    async def get_blocked_users(self):
        query = await self.session.execute(
            select(User).where(User.is_blocked == True)
        )
        result = query.scalars().all()
        return parse_obj_as(list[UserDTO], result)

    async def get_admins(self):
        query = select(User).where(User.is_admin == True)
        result = (await self.session.execute(query))
        admins = result.scalars().all()
        return parse_obj_as(list[UserDTO], admins)

    async def get_user_balance(self, user_id: int):
        query = select(User).where(User.user_id == user_id)
        result = (await self.session.execute(query))
        user = result.scalars().all()
        return parse_obj_as(list[UserDTO], user)
