# src/api/auth.py

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import models
from ..db.session import get_db
from ..schemas import user as schemas_user # FIX: استفاده از شمای Pydantic
from ..core import security 

router = APIRouter(prefix="/auth", tags=["Authentication"])


# 1. روتر ثبت نام (POST /auth/register)
@router.post("/register", response_model=schemas_user.User) 
def register_user(
    user_in: schemas_user.UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    ثبت نام کاربر جدید و بازگرداندن اطلاعات کاربر (شامل API Key).
    """
    # 1. بررسی وجود کاربر
    user = db.execute(select(models.User).filter(models.User.email == user_in.email)).scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # 2. هش کردن رمز عبور
    hashed_password = security.get_password_hash(user_in.password)

    # 3. ایجاد API Key منحصر به فرد
    api_key = security.create_api_key()
    
    # 4. ذخیره کاربر در دیتابیس
    db_user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        api_key=api_key,
        is_superuser=user_in.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# 2. روتر دریافت توکن (POST /auth/access-token)
@router.post("/access-token", response_model=schemas_user.Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    دریافت توکن JWT برای ورود.
    """
    user = db.execute(select(models.User).filter(models.User.email == form_data.username)).scalar_one_or_none()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
        
    return {
        "access_token": security.create_access_token(subject=user.email),
        "token_type": "bearer",
    }
