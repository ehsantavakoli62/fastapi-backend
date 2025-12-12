# src/schemas/user.py
# طرح‌واره‌های Pydantic برای مدل User

from pydantic import BaseModel, Field


# Base Schema: شامل فیلدهایی که در همه جا (حتی در پاسخ‌ها) استفاده می‌شوند
class UserBase(BaseModel):
    email: str = Field(..., example="test@example.com")
    is_active: bool = True
    is_superuser: bool = False

    # پیکربندی: برای فعال کردن سازگاری با مدل‌های ORM (SQLAlchemy)
    class Config:
        # Pydantic V1 syntax
        orm_mode = True
        # Pydantic V2 syntax (برای تضمین سازگاری)
        from_attributes = True


# Schema برای ثبت نام: نیاز به ایمیل، رمز عبور و پرمیشن‌ها
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="StrongPassword123")


# Schema برای پاسخ (Response Model): شامل ID است
class User(UserBase):
    id: int = Field(..., example=1)
