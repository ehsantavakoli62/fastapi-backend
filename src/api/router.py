# src/api/router.py

from fastapi import APIRouter

# وارد کردن روترهای موجود
from . import auth

# وارد کردن روترهای جدید
from . import tweet
from . import media
from . import user_profile


router = APIRouter()


# اضافه کردن روترهای موجود (احراز هویت)
router.include_router(auth.router)

# اضافه کردن روترهای جدید (عملیات میکروبلاگ)
router.include_router(tweet.router)
router.include_router(media.router)
router.include_router(user_profile.router)
