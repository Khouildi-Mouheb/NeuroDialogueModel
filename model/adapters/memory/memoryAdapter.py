from domain.ports.memoryPort import MemoryPort
from domain.memory.database import SessionLocal
from domain.memory.models import ConversationMemory
from typing import Optional
import datetime

class PostgresMemoryAdapter(MemoryPort):

    def getSummary(self, user_id: str, chat_id: str) -> Optional[str]:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            return record.summary if record else None

    def getProfile(self, user_id: str, chat_id: str) -> Optional[str]:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            return record.profile if record else None

    def updateSummary(self, user_id: str, chat_id: str, summary: str) -> None:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            if record:
                record.summary = summary
                record.updated_at = datetime.datetime.utcnow()
            else:
                session.add(ConversationMemory(
                    user_id=user_id,
                    chat_id=chat_id,
                    summary=summary
                ))
            session.commit()

    def updateMemory(self, user_id: str, chat_id: str, summary: str, profile: str) -> None:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            if record:
                record.summary = summary
                record.profile = profile
                record.updated_at = datetime.datetime.utcnow()
            else:
                session.add(ConversationMemory(
                    user_id=user_id,
                    chat_id=chat_id,
                    summary=summary,
                    profile=profile
                ))
            session.commit()