# src/api/router.py

from fastapi import APIRouter
from . import auth

# ایجاد نمونه APIRouter
# تمام مسیرها تحت پیشوند /api/v1 قرار می‌گیرند
router = APIRouter(prefix="/api/v1")

# افزودن روتر احراز هویت
router.include_router(auth.router)


@router.get("/status")
def get_status():
    """
    مسیر تست سلامت برنامه
    """
    return {"status": "ok", "message": "API is running"}
