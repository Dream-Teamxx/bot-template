import logging

from sqlalchemy import select, func, insert, update

from infrastructure.database.models.bot_status import BotStatus
from infrastructure.database.models.user import User

logger = logging.getLogger(__name__)


class Repo:
    """Db abstraction layer"""

    def __init__(self, session):
        self.session = session

    async def get_admins(self):
        sql = select(User.user_id).where(User.is_admin == True)
        result = (await self.session.execute(sql)).all()
        return result

    async def update_user_if_not_exists(self, user_id: int, full_name: str, registered_at):
        sql = select(User.user_id).where(User.user_id == user_id)
        result = (await self.session.execute(sql)).first()
        if not result:
            logger.info(f'User {user_id} not found in db, creating new')
            await self.session.execute(
                insert(User).values(user_id=user_id, full_name=full_name, registered_at=registered_at))
            await self.session.commit()

    async def get_user_stats(self):
        sql = select(func.count(User.user_id))
        result = (await self.session.execute(sql)).all()
        return result

    async def get_bot_status(self):
        sql = select(BotStatus.status).where(BotStatus.id == 1)
        result = (await self.session.execute(sql)).first()
        return result

    async def set_maintenance(self):
        await self.session.execute(
            update(BotStatus).where(BotStatus.id == 1).values(status='maintenance')
        )
        await self.session.commit()

    async def disable_maintenance(self):
        await self.session.execute(
            update(BotStatus).where(BotStatus.id == 1).values(status='normal')
        )
        await self.session.commit()
