# Dockerfile

# استفاده از ایمیج پایه پایتون 3.11-slim
FROM python:3.11-slim

# تنظیم متغیر محیطی برای جلوگیری از بافرینگ خروجی پایتون
ENV PYTHONUNBUFFERED 1

# تنظیم دایرکتوری کاری داخل کانتینر
WORKDIR /app

# کپی کردن فایل نیازمندی‌ها و نصب وابستگی‌ها
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کد سورس برنامه
# توجه: این دستور پوشه src را به داخل کانتینر کپی می‌کند
COPY ./src /app/src

# تعریف دستوری که در زمان اجرای کانتینر اجرا می‌شود
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
