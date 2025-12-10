
# src/schemas/user.py

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """مدل پایه برای تعریف فیلدهای مشترک کاربران"""
    email: EmailStr
    is_active: bool | None = True
    is_superuser: bool | None = False


class UserCreate(UserBase):
    """مدل مورد نیاز برای ثبت نام کاربر جدید (شامل رمز عبور)"""
    password: str


class UserUpdate(UserBase):
    """مدل مورد نیاز برای به‌روزرسانی اطلاعات کاربر"""
    password: str | None = None


class UserInDBBase(UserBase):
    """مدل پایه برای خواندن اطلاعات کاربر از پایگاه داده"""
    id: int | None = None

    class Config:
        """تنظیمات برای سازگاری با SQLAlchemy (اجازه خواندن از ORM)"""
        from_attributes = True


class User(UserInDBBase):
    """مدل نهایی برای نمایش اطلاعات کاربر به کاربران دیگر"""
    pass
