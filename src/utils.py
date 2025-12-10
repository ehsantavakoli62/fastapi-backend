# src/utils.py
# توابع مورد نیاز برای هش کردن رمز عبور و کار با زمان (Skillbox)

from passlib.context import CryptContext
from datetime import datetime, timedelta

# تنظیمات هش کردن رمز عبور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """هش کردن رمز عبور"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی صحت رمز عبور"""
    return pwd_context.verify(plain_password, hashed_password)
