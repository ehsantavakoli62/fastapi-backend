# src/main.py

from fastapi import FastAPI
from .api import router as api_router

# ایجاد نمونه FastAPI
app = FastAPI(
    title="FastAPI Skillbox Project",
    description="Backend service for user authentication and management.",
    version="1.0.0",
)

# اضافه کردن روتر اصلی
# روترها تمام مسیرهای API ما را شامل می‌شوند.
app.include_router(api_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend (Skillbox)"}
