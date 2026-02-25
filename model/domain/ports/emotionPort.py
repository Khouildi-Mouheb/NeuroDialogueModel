from abc import ABC , abstractmethod
from domain.valueObjects.emotionResult import EmotionResult

class EmotionPort(ABC):
    @abstractmethod
    def detectEmotions(self, text: str, top_k: int = 3) -> EmotionResult:
        pass

    @abstractmethod
    def getEmotionalSummary(self, text: str) -> dict:
        pass

    @abstractmethod
    def formatForCoach(self, text: str) -> str:
        pass