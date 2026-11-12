from abc import ABC, abstractmethod
from typing import Optional
from domain.memory.enums.coachingStage import CoachingStage
from domain.memory.enums.tagPriority import TagPriority


class MemoryPort(ABC):

    # -------------------------------------------------------------------------
    # ConversationMemory
    # -------------------------------------------------------------------------

    @abstractmethod
    def getSummary(self, user_id: str, chat_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def getProfile(self, user_id: str, chat_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def updateMemory(self, user_id: str, chat_id: str, summary: str, profile: str) -> None:
        pass

    # -------------------------------------------------------------------------
    # UserProfile
    # -------------------------------------------------------------------------

    @abstractmethod
    def getUserProfile(self, user_id: str):
        pass

    @abstractmethod
    def upsertUserProfile(
        self,
        user_id: str,
        summary: Optional[str] = None,
        profile: Optional[str] = None,
        preferedCommunicationStyle: Optional[str] = None,
        emotionalStabilityScore: Optional[float] = None,
        personalityType: Optional[str] = None,
        coachingStage: Optional[CoachingStage] = None,
    ) -> None:
        pass

    # -------------------------------------------------------------------------
    # UserStrength
    # -------------------------------------------------------------------------

    @abstractmethod
    def addStrength(self, user_id: str, emotionLabel: str, frequency: int = 1) -> None:
        pass

    @abstractmethod
    def getStrengths(self, user_id: str) -> list:
        pass

    # -------------------------------------------------------------------------
    # CoachingTag
    # -------------------------------------------------------------------------

    @abstractmethod
    def addCoachingTag(self, user_id: str, tag: str, priority: TagPriority) -> None:
        pass

    @abstractmethod
    def getCoachingTags(self, user_id: str) -> list:
        pass

    # -------------------------------------------------------------------------
    # UserEmotion
    # -------------------------------------------------------------------------

    @abstractmethod
    def addEmotion(self, user_id: str, emotionLabel: str, intensity: Optional[float] = None) -> None:
        pass

    @abstractmethod
    def getEmotionHistory(self, user_id: str) -> list:
        pass

    # -------------------------------------------------------------------------
    # CoachingSession
    # -------------------------------------------------------------------------

    @abstractmethod
    def addCoachingSession(
        self,
        user_id: str,
        chat_id: str,
        coachingStage: Optional[CoachingStage] = None,
        goalFocus: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def getCoachingSessions(self, user_id: str) -> list:
        pass

    @abstractmethod
    def updateCoachingSession(
        self,
        session_id: int,
        goalFocus: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> None:
        pass