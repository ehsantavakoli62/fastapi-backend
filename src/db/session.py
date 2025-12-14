# src/db/session.py

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

# Create engine for connecting to the PostgreSQL database
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

# Configure session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()