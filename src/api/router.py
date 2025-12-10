# src/api/router.py

from fastapi import APIRouter

# ایجاد نمونه APIRouter
router = APIRouter()


@router.get("/status")
def get_status():
    """
    مسیر تست سلامت برنامه
    """
    return {"status": "ok", "message": "API is running"}
