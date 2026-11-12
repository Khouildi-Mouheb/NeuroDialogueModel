import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MEMORY_DB_URL")

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
Base         = declarative_base()

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    from domain.memory.models import (
        ConversationMemory,
        UserProfile,
        UserStrength,
        CoachingTag,
        UserEmotion,
        CoachingSession,
    )
    Base.metadata.create_all(bind=engine)