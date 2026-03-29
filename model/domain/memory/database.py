import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MEMORY_DB_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def init_db():
    from domain.memory.models import ConversationMemory
    Base.metadata.create_all(bind=engine)

    # Ensure 'profile' column exists (Lightweight migration)
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('conversation_memory')]
    if 'profile' not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE conversation_memory ADD COLUMN profile TEXT"))