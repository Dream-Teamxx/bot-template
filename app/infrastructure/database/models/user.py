from sqlalchemy import BigInteger, Column, String, DateTime, Boolean

from infrastructure.database.base import Base


class User(Base):
    __tablename__ = 'users'
    __tableargs__ = {'extend_existing': True}

    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(255))
    username = Column(String(255))
    registered_at = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
