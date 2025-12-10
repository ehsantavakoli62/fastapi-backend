# src/db/__init__.py

# این import ها ضروری هستند تا مدل‌های ORM در Base ثبت شوند.
from .base import Base
from .models import User
from .session import SessionLocal, engine
