# src/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # تنظیمات پایگاه داده
    POSTGRES_USER: str = "fastapi_user"
    POSTGRES_PASSWORD: str = "fastapi_password"
    POSTGRES_SERVER: str = "postgres_db"  # نام سرویس دیتابیس در docker-compose.yml
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "fastapi_db"

    # رشته اتصال به دیتابیس
    SQLALCHEMY_DATABASE_URL: str

    # تنظیمات JWT (رمز عبور و الگوریتم)
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY"  # این را باید در محیط واقعی تغییر دهید
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 روز

    # نام و آدرس پروژه
    PROJECT_NAME: str = "FastAPI Skillbox Project"

    # تنظیمات کلاس BaseSettings
    class Config:
        case_sensitive = True


# ایجاد یک نمونه از کلاس Settings برای استفاده در سراسر برنامه
settings = Settings()

# محاسبه SQLALCHEMY_DATABASE_URL پس از بارگذاری تنظیمات
settings.SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)