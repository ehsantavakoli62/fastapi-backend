# src/api/tweet.py

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, insert, delete
from datetime import datetime

from ..db import models
from ..schemas.user import TweetCreate, TweetCreateResponse, TweetListResponse, TweetResponseBase, StatusResponse
from .deps import get_db, get_current_user_by_api_key

router = APIRouter(tags=["Tweets"])


def get_tweet_by_id(db: Session, tweet_id: int) -> models.Tweet:
    """دریافت توییت بر اساس ID، یا پرتاب 404"""
    tweet = db.execute(select(models.Tweet).filter(models.Tweet.id == tweet_id)).scalar_one_or_none()
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found."
        )
    return tweet


# 1. روتر ایجاد توییت (POST /api/tweets)
@router.post("/tweets", response_model=TweetCreateResponse)
def create_tweet(
    tweet_in: TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key), 
) -> Any:
    """
    ایجاد یک توییت جدید.
    """
    
    # 1. ایجاد مدل توییت
    db_tweet = models.Tweet(
        content=tweet_in.tweet_data,
        author_id=current_user.id,
        created_at=datetime.utcnow()
    )

    # 2. اتصال فایل‌های رسانه‌ای (در صورت وجود)
    if tweet_in.tweet_media_ids:
        media_files = db.execute(
            select(models.Media).filter(models.Media.id.in_(tweet_in.tweet_media_ids))
        ).scalars().all()
        
        if len(media_files) != len(tweet_in.tweet_media_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more media IDs are invalid."
            )
            
        db_tweet.attachments.extend(media_files)

    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    return {"result": True, "tweet_id": db_tweet.id}


# 2. روتر دریافت فید (GET /api/tweets)
@router.get("/tweets", response_model=TweetListResponse)
def get_feed(db: Session = Depends(get_db)) -> Any:
    """
    دریافت فید تمام توییت‌ها (شامل لایک‌ها و مدیا).
    """
    # دریافت همه توییت‌ها به ترتیب زمان (جدیدترین اول)
    tweets = db.execute(
        select(models.Tweet)
        .order_by(desc(models.Tweet.created_at))
    ).scalars().all()

    # تبدیل مدل‌های دیتابیس به شمای پاسخ
    # این تابع به صورت خودکار اطلاعات author, attachments و likes را از روابط SQLAlchemy دریافت می‌کند
    tweet_responses = [
        TweetResponseBase.model_validate(tweet)
        for tweet in tweets
    ]

    return {"result": True, "tweets": tweet_responses}


# 3. روتر حذف توییت (DELETE /api/tweets/<id>)
@router.delete("/tweets/{tweet_id}", response_model=TweetCreateResponse)
def delete_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    حذف یک توییت توسط نویسنده آن.
    """
    tweet = get_tweet_by_id(db, tweet_id)

    # بررسی مجوز: فقط نویسنده می‌تواند توییت را حذف کند
    if tweet.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this tweet."
        )

    db.delete(tweet)
    db.commit()

    return {"result": True, "tweet_id": tweet_id}


# --- توابع لایک ---

# 4. روتر لایک کردن توییت (POST /api/tweets/<id>/likes)
@router.post("/tweets/{tweet_id}/likes", response_model=StatusResponse)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    لایک کردن یک توییت.
    """
    tweet = get_tweet_by_id(db, tweet_id)
    
    # بررسی کنید که آیا قبلاً لایک شده است
    if current_user in tweet.likes:
        return {"result": True} # قبلاً لایک شده، نیازی به عملیات نیست
        
    # اضافه کردن لایک (اضافه کردن کاربر به لیست لایک‌های توییت)
    tweet.likes.append(current_user)
    db.commit()

    return {"result": True}


# 5. روتر آن‌لایک کردن توییت (DELETE /api/tweets/<id>/likes)
@router.delete("/tweets/{tweet_id}/likes", response_model=StatusResponse)
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_by_api_key),
) -> Any:
    """
    حذف لایک یک توییت.
    """
    tweet = get_tweet_by_id(db, tweet_id)
    
    # بررسی کنید که آیا قبلاً لایک شده است
    if current_user not in tweet.likes:
        return {"result": True} # لایک نشده، نیازی به عملیات نیست

    # حذف لایک (حذف کاربر از لیست لایک‌های توییت)
    tweet.likes.remove(current_user)
    db.commit()
    
    return {"result": True}
