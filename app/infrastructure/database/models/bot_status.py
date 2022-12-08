from sqlalchemy import Column, String, Integer

from infrastructure.database.base import Base


class BotStatus(Base):
    __tablename__ = 'bot_status'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(255), nullable=False)
