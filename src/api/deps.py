# src/api/deps.py
# این فایل شامل توابع مورد نیاز برای مدیریت JWT و Session پایگاه داده است.

import os
from datetime import datetime, timedelta
from typing import Generator, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..schemas.token import TokenPayload


# تنظیمات JWT را از متغیرهای محیطی می‌خوانیم
SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)


# تعریف طرح امنیتی OAuth2
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """توابع وابستگی برای دریافت Session دیتابیس (Dependency)"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def create_access_token(subject: str | Any, expires_delta: timedelta = None) -> str:
    """ایجاد توکن دسترسی (Access Token)"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # اگر زمان انقضا مشخص نشد، از متغیر محیطی استفاده کن
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str = Depends(reusable_oauth2)) -> TokenPayload:
    """اعتبارسنجی و دیکد کردن توکن و برگرداندن Payload"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        # استفاده از مدل Pydantic برای اعتبارسنجی ساختار Payload
        token_data = TokenPayload(user_id=payload.get("sub"))
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # اگر user_id در توکن موجود نباشد یا مقدار آن None باشد
    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials (invalid user_id)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data
