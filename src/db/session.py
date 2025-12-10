# src/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. تعریف آدرس اتصال به پایگاه داده
# از متغیرهای محیطی که در Docker-Compose تعریف می‌کنیم استفاده می‌شود
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/app"
)

# 2. ایجاد Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # در محیط پروداکشن، این خط باید False باشد
    pool_pre_ping=True
)

# 3. ایجاد SessionLocal
# این شیء برای ایجاد یک Session برای هر درخواست استفاده می‌شود
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
