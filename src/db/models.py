# src/db/models.py
# تعریف مدل‌های ORM

from sqlalchemy import Boolean, Column, Integer, String
from .base import Base


class User(Base):
    """
    مدل SQLAlchemy برای جدول 'user'
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
