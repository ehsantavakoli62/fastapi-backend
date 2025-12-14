# src/api/media.py

import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any

from ..db import models
from ..schemas.user import MediaResponse, StatusResponse
from .deps import get_db, get_current_user_by_api_key

router = APIRouter(tags=["Media"])

# مسیر محلی برای ذخیره فایل‌ها
MEDIA_ROOT = "media"

# مطمئن می‌شویم که پوشه ذخیره‌سازی وجود داشته باشد
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)


@router.post("/medias", response_model=MediaResponse)
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # نیاز به اعتبارسنجی کاربر برای آپلود
    current_user: models.User = Depends(get_current_user_by_api_key), 
) -> Any:
    """
    آپلود یک فایل رسانه‌ای (تصویر).
    """
    
    # 1. ساخت مسیر ذخیره‌سازی
    # از UUID یا هش برای نام‌گذاری مطمئن استفاده می‌شود (اینجا برای سادگی از ID + نام فایل)
    # در محیط واقعی، باید نام فایل را امن کنیم
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "file"
    # نام فایل موقت را بر اساس زمان فعلی و user ID می‌سازیم
    temp_filename = f"{current_user.id}_{int(os.time())}.{file_extension}" 
    file_path = os.path.join(MEDIA_ROOT, temp_filename)
    
    # 2. ذخیره فایل روی سیستم فایل
    try:
        with open(file_path, "wb") as buffer:
            # کپی کردن محتوای فایل آپلود شده به فایل محلی
            for chunk in file.file:
                buffer.write(chunk)
    except Exception as e:
        # در صورت بروز خطا در ذخیره فایل
        print(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save media file."
        )

    # 3. ایجاد رکورد در دیتابیس
    db_media = models.Media(
        file_path=file_path,
        file_type=file.content_type,
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    return {"result": True, "media_id": db_media.id}


@router.get("/medias/{media_id}")
def get_media(
    media_id: int,
    db: Session = Depends(get_db),
    # این روتر نیاز به کاربر احراز هویت شده ندارد، چون فایل‌ها عمومی هستند
) -> Any:
    """
    دریافت یک فایل رسانه‌ای (تصویر) بر اساس ID آن.
    """
    media = db.execute(
        select(models.Media).filter(models.Media.id == media_id)
    ).scalar_one_or_none()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found."
        )
        
    # ارسال فایل به عنوان پاسخ
    return FileResponse(media.file_path, media_type=media.file_type)
