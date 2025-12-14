# src/schemas/user.py

from typing import List, Optional, Any
from pydantic import BaseModel, Field


# --- Schemas for User (Auth and Profile) ---

# شمای مورد نیاز برای ثبت نام (شامل نام برای نمایش در فید)
class UserCreate(BaseModel):
    name: str = Field(..., example="Cool Dev")
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="secure_password")
    is_superuser: bool = False


# شمای پایه برای نمایش اطلاعات کاربر (درون توییت یا لیست)
class UserBase(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Cool Dev")

    class Config:
        from_attributes = True


# شمای کامل کاربر که در پاسخ ثبت نام و GET /api/users/<id> استفاده می‌شود.
class User(UserBase):
    # لیست کاربران فالور (بر اساس شمای پایه)
    followers: List[UserBase] = Field(default_factory=list)  # اصلاح شده
    # لیست کاربرانی که فالو کرده است (بر اساس شمای پایه)
    following: List[UserBase] = Field(default_factory=list)  # اصلاح شده


# شمای GET /api/users/me (تنها برای API Key)
class UserMe(BaseModel):
    result: bool = Field(..., example=True)
    user: User

    class Config:
        from_attributes = True


# --- Schemas for Media ---

# شمای پاسخ برای آپلود مدیا (POST /api/medias)
class MediaResponse(BaseModel):
    result: bool = Field(..., example=True)
    media_id: int = Field(..., example=1)


# شمای پایه برای نمایش مدیا در خروجی توییت
class MediaBase(BaseModel):
    id: int = Field(..., example=1)
    url: str = Field(..., example="/api/medias/1")  # آدرس URL محلی فایل

    class Config:
        from_attributes = True


# --- Schemas for Tweets ---

# شمای مورد نیاز برای ایجاد توییت (POST /api/tweets)
class TweetCreate(BaseModel):
    tweet_data: str = Field(..., example="This is my first tweet!")
    # لیست اختیاری ID های مدیا که قبلاً آپلود شده‌اند
    tweet_media_ids: Optional[List[int]] = Field(None, example=[1, 2])


# شمای لایک (برای نمایش در لیست لایک‌های توییت)
class LikeBase(BaseModel):
    user_id: int = Field(..., example=1)
    name: str = Field(..., example="Cool Dev")

    class Config:
        from_attributes = True


# شمای پایه برای نمایش یک توییت در فید یا خروجی API
class TweetResponseBase(BaseModel):
    id: int = Field(..., example=1)
    content: str = Field(..., example="This is my first tweet!")
    # Attachments اکنون به جای لیست لینک‌ها، لیست شمای مدیا است
    attachments: List[MediaBase] = Field(default_factory=list)  # اصلاح شده
    author: UserBase
    likes: List[LikeBase] = Field(default_factory=list)  # اصلاح شده

    class Config:
        from_attributes = True


# شمای پاسخ برای ایجاد توییت (POST /api/tweets)
class TweetCreateResponse(BaseModel):
    result: bool = Field(..., example=True)
    tweet_id: int = Field(..., example=1)


# شمای پاسخ برای فید اصلی (GET /api/tweets)
class TweetListResponse(BaseModel):
    result: bool = Field(..., example=True)
    tweets: List[TweetResponseBase] = Field(default_factory=list)  # اصلاح شده


# --- شمای پایه برای پاسخ‌های وضعیت (Status Responses) ---

# شمای پاسخ موفقیت‌آمیز برای عملیات‌هایی مانند لایک، فالو، حذف
class StatusResponse(BaseModel):
    result: bool = Field(..., example=True)


# شمای پاسخ خطا (بر اساس سند Skillbox)
class ErrorResponse(BaseModel):
    result: bool = Field(..., example=False)
    error_type: str = Field(..., example="NotFound")
    error_message: str = Field(..., example="Tweet not found.")