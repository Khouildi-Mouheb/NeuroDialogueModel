from .database import Base
from sqlalchemy import Column, Integer, Text, DateTime , String
from datetime import datetime

class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(String, nullable=False, index=True)
    chat_id    = Column(String, nullable=False, index=True)
    summary    = Column(Text, nullable=True)
    profile    = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)