# tests/test_api.py

import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.main import app
from src.db.session import get_db
from src.db import models


# --- تنظیمات دیتابیس تستی ---
# از یک URL دیتابیس تستی (SQLite در حافظه) استفاده می‌کنیم
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ایجاد تمام جداول در دیتابیس تستی
Base.metadata.create_all(bind=engine)


# --- بازنویسی get_db برای استفاده از دیتابیس تستی ---
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# --- فیکسچر برای پاکسازی دیتابیس قبل از هر تست ---
@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """بعد از هر تست، تمام داده‌های جدول Users را پاک می‌کند."""
    # Base.metadata.drop_all(bind=engine) 
    # Base.metadata.create_all(bind=engine)
    # برای جلوگیری از خطاهای foreign key، فقط داده‌های User را پاک می‌کنیم
    
    # برای این تست‌ها کافی است چون هر تست جداگانه User می‌سازد
    
    # بعد از هر تست، داده‌های تمام جداول را پاک می‌کنیم تا جداول خالی باشند
    db = TestingSessionLocal()
    
    # پاک کردن داده‌ها با رعایت ترتیب وابستگی
    db.execute(models.likes_table.delete())
    db.execute(models.follows_table.delete())
    db.execute(models.tweet_media_table.delete())
    db.execute(models.Tweet.delete())
    db.execute(models.Media.delete())
    db.execute(models.User.delete())
    db.commit()
    db.close()


# --- متغیرهای تستی ---
TEST_USER = {
    "name": "TestUser",
    "email": "test@example.com",
    "password": "testpassword",
    "is_superuser": False
}

TEST_USER_2 = {
    "name": "TestUser2",
    "email": "test2@example.com",
    "password": "testpassword2",
    "is_superuser": False
}


# --- توابع کمکی ---

def register_user_and_get_api_key(user_data: dict) -> str:
    """ثبت نام کاربر و بازگرداندن API Key."""
    # 1. ثبت نام
    register_response = client.post(
        "/auth/register",
        json=user_data
    )
    assert register_response.status_code == 200
    
    # 2. دریافت توکن
    token_response = client.post(
        "/auth/access-token",
        data={"username": user_data["email"], "password": user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert token_response.status_code == 200
    access_token = token_response.json()["access_token"]
    
    # 3. دریافت API Key با استفاده از توکن
    me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200
    return me_response.json()["user"]["api_key"]


# --- تست‌های اصلی (API Testing) ---

# T1: تست ثبت نام موفق و API Key
def test_register_and_api_key_retrieval():
    """تست ثبت نام، ورود، و دریافت API Key."""
    api_key = register_user_and_get_api_key(TEST_USER)
    assert api_key is not None
    assert isinstance(api_key, str)


# T2: تست احراز هویت با API Key
def test_authentication_with_api_key():
    """تست دسترسی به مسیر محافظت شده با API Key."""
    api_key = register_user_and_get_api_key(TEST_USER)
    
    response = client.get(
        "/users/me",
        headers={"Api-Key": api_key}
    )
    
    assert response.status_code == 200
    assert response.json()["user"]["name"] == TEST_USER["name"]
    assert response.json()["user"]["api_key"] == api_key


# T3: تست ایجاد توییت
def test_create_tweet():
    """تست ایجاد موفقیت‌آمیز توییت و ظاهر شدن آن در فید."""
    api_key = register_user_and_get_api_key(TEST_USER)
    tweet_data = "Hello Skillbox!"
    
    response = client.post(
        "/tweets",
        json={"tweet_data": tweet_data, "tweet_media_ids": []},
        headers={"Api-Key": api_key}
    )
    
    assert response.status_code == 200
    assert response.json()["result"] is True
    tweet_id = response.json()["tweet_id"]
    
    # چک کردن فید
    feed_response = client.get("/tweets")
    assert feed_response.status_code == 200
    assert len(feed_response.json()["tweets"]) == 1
    assert feed_response.json()["tweets"][0]["content"] == tweet_data
    assert feed_response.json()["tweets"][0]["author"]["name"] == TEST_USER["name"]
    assert feed_response.json()["tweets"][0]["id"] == tweet_id


# T4: تست لایک کردن توییت
def test_like_tweet():
    """تست لایک کردن و نمایش لایک در فید."""
    user1_key = register_user_and_get_api_key(TEST_USER)
    user2_key = register_user_and_get_api_key(TEST_USER_2)
    
    # کاربر 1 توییت می‌سازد
    create_response = client.post(
        "/tweets",
        json={"tweet_data": "Like me!", "tweet_media_ids": []},
        headers={"Api-Key": user1_key}
    )
    tweet_id = create_response.json()["tweet_id"]
    
    # کاربر 2 لایک می‌کند
    like_response = client.post(
        f"/tweets/{tweet_id}/likes",
        headers={"Api-Key": user2_key}
    )
    assert like_response.status_code == 200
    assert like_response.json()["result"] is True
    
    # چک کردن فید برای لایک
    feed_response = client.get("/tweets")
    assert len(feed_response.json()["tweets"][0]["likes"]) == 1
    assert feed_response.json()["tweets"][0]["likes"][0]["name"] == TEST_USER_2["name"]
    
    # کاربر 2 آن‌لایک می‌کند
    unlike_response = client.delete(
        f"/tweets/{tweet_id}/likes",
        headers={"Api-Key": user2_key}
    )
    assert unlike_response.status_code == 200
    assert unlike_response.json()["result"] is True
    
    # چک کردن فید بعد از آن‌لایک
    feed_response_after = client.get("/tweets")
    assert len(feed_response_after.json()["tweets"][0]["likes"]) == 0


# T5: تست فالو کردن کاربر
def test_follow_user():
    """تست فالو، آنفالو و نمایش در پروفایل."""
    user1_key = register_user_and_get_api_key(TEST_USER)
    user2_key = register_user_and_get_api_key(TEST_USER_2)
    
    db = TestingSessionLocal()
    user2_model = db.execute(select(models.User).filter(models.User.email == TEST_USER_2["email"])).scalar_one()
    user2_id = user2_model.id
    db.close()
    
    # کاربر 1، کاربر 2 را فالو می‌کند
    follow_response = client.post(
        f"/users/{user2_id}/follow",
        headers={"Api-Key": user1_key}
    )
    assert follow_response.status_code == 200
    assert follow_response.json()["result"] is True
    
    # چک کردن پروفایل کاربر 1 (باید user2 در following باشد)
    user1_profile = client.get("/users/me", headers={"Api-Key": user1_key})
    assert len(user1_profile.json()["user"]["following"]) == 1
    assert user1_profile.json()["user"]["following"][0]["name"] == TEST_USER_2["name"]
    
    # چک کردن پروفایل کاربر 2 (باید user1 در followers باشد)
    user2_profile = client.get(f"/users/{user2_id}", headers={"Api-Key": user1_key})
    assert len(user2_profile.json()["user"]["followers"]) == 1
    assert user2_profile.json()["user"]["followers"][0]["name"] == TEST_USER["name"]
    
    # کاربر 1، کاربر 2 را آنفالو می‌کند
    unfollow_response = client.delete(
        f"/users/{user2_id}/follow",
        headers={"Api-Key": user1_key}
    )
    assert unfollow_response.status_code == 200
    assert unfollow_response.json()["result"] is True
    
    # چک کردن پروفایل کاربر 1 بعد از آنفالو
    user1_profile_after = client.get("/users/me", headers={"Api-Key": user1_key})
    assert len(user1_profile_after.json()["user"]["following"]) == 0
