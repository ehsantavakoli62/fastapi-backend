# src/api/user_profile.py

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from ..db import models
from ..schemas.user import User, StatusResponse, UserMe
from .deps import get_db, get_current_user_by_api_key

router = APIRouter(tags=["User Profile and Follow"])


# تابع کمکی برای یافتن کاربر
def get_user_by_id(db: Session, user_id: int) -> models.User:
    """دریافت کاربر بر اساس ID، یا پرتاب 404"""
    user = db.execute(select(models.User).filter(models.User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user


# 1. روتر دریافت پروفایل کاربر (GET /api/users/me)
@router.get("/users/me", response_model=UserMe)
def read_user_me(
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    دریافت اطلاعات پروفایل کاربر احراز هویت شده.
    """
    # مدل User در شمای ما شامل followers و following است که SQLAlchemy به صورت خودکار پر می‌کند
    return {"result": True, "user": current_user}


# 2. روتر دریافت پروفایل کاربر دیگر (GET /api/users/<id>)
@router.get("/users/{user_id}", response_model=UserMe)
def read_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    # نیاز به احراز هویت برای دیدن پروفایل عمومی
    current_user: models.User = Depends(get_current_user_by_api_key), 
) -> Any:
    """
    دریافت اطلاعات پروفایل یک کاربر دیگر.
    """
    user = get_user_by_id(db, user_id)
    return {"result": True, "user": user}


# 3. روتر فالو کردن (POST /api/users/<id>/follow)
@router.post("/users/{user_id}/follow", response_model=StatusResponse)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    دنبال کردن یک کاربر.
    """
    user_to_follow = get_user_by_id(db, user_id)
    
    # اطمینان از اینکه کاربر خودش را دنبال نکند
    if current_user.id == user_to_follow.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself."
        )
    
    # بررسی کنید که آیا قبلاً دنبال شده است
    if user_to_follow in current_user.following:
        # اگر قبلاً دنبال شده، موفقیت را برمی‌گردانیم
        return {"result": True} 

    # اگر دنبال نشده، اضافه می‌کنیم
    current_user.following.append(user_to_follow)
    db.commit()

    return {"result": True}


# 4. روتر آنفالو کردن (DELETE /api/users/<id>/follow)
@router.delete("/users/{user_id}/follow", response_model=StatusResponse)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    لغو دنبال کردن یک کاربر.
    """
    user_to_unfollow = get_user_by_id(db, user_id)
    
    # بررسی کنید که آیا کاربر، کاربر مورد نظر را دنبال می‌کند
    if user_to_unfollow not in current_user.following:
        # اگر دنبال نمی‌کند، موفقیت را برمی‌گردانیم
        return {"result": True} 

    # اگر دنبال می‌کند، حذف می‌کنیم
    current_user.following.remove(user_to_unfollow)
    db.commit()

    return {"result": True}
