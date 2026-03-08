from abc import ABC, abstractmethod
from typing import Optional

class MemoryPort(ABC):

    @abstractmethod
    def getSummary(self, user_id: int, chat_id: int) -> Optional[str]:
        pass

    @abstractmethod
    def updateSummary(self, user_id: int, chat_id: int, summary: str) -> None:
        pass