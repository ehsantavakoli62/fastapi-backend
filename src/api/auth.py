# src/api/auth.py

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import models
from ..db.session import SessionLocal
from ..schemas.token import Token
from ..schemas.user import UserCreate
from ..utils import get_password_hash, verify_password
from .deps import get_db, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/auth", tags=["auth"])


# تابع کمکی برای اعتبارسنجی کاربر
def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """اعتبارسنجی کاربر بر اساس ایمیل و رمز عبور"""
    user = db.execute(select(models.User).filter(models.User.email == email)).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/register", response_model=models.User)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    ثبت نام کاربر جدید.
    در صورت وجود ایمیل، خطا می‌دهد.
    """
    user = db.execute(select(models.User).filter(models.User.email == user_in.email)).scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    # هش کردن رمز عبور
    hashed_password = get_password_hash(user_in.password)
    
    # ایجاد مدل کاربر جدید
    db_user = models.User(
        email=user_in.email, 
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=user_in.is_superuser
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/access-token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    دریافت توکن دسترسی OAuth2 برای ورود کاربر.
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ایجاد توکن دسترسی
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
