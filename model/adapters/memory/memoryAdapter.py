from domain.ports.memoryPort import MemoryPort
from domain.memory.database import SessionLocal
from domain.memory.models import ConversationMemory
from typing import Optional
import datetime

class PostgresMemoryAdapter(MemoryPort):

    def getSummary(self, user_id: int, chat_id: int) -> Optional[str]:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            return record.summary if record else None

    def updateSummary(self, user_id: int, chat_id: int, summary: str) -> None:
        with SessionLocal() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id,
                chat_id=chat_id
            ).first()
            if record:
                record.summary = summary
                record.updated_at = datetime.utcnow()
            else:
                session.add(ConversationMemory(
                    user_id=user_id,
                    chat_id=chat_id,
                    summary=summary
                ))
            session.commit()