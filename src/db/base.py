# src/db/base.py
# تعریف کلاس پایه برای مدل‌های SQLAlchemy

from sqlalchemy.orm import declarative_base

# Base یک کلاس پایه است که تمام مدل‌های ORM ما از آن ارث خواهند برد
Base = declarative_base()
