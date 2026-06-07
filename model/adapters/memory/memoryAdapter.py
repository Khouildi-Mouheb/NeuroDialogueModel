from domain.ports.memoryPort import MemoryPort
from domain.memory.database import get_session
from domain.memory.models import (
    ConversationMemory,
    UserProfile,
    UserStrength,
    CoachingTag,
    UserEmotion,
    CoachingSession,
)
from domain.memory.enums.coachingStage import CoachingStage
from domain.memory.enums.tagPriority import TagPriority
from typing import Optional
import datetime


class PostgresMemoryAdapter(MemoryPort):

    # -------------------------------------------------------------------------
    # ConversationMemory
    # -------------------------------------------------------------------------

    def getSummary(self, user_id: str, chat_id: str) -> Optional[str]:
        with get_session() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id, chat_id=chat_id
            ).first()
            return record.summary if record else None

    def getProfile(self, user_id: str, chat_id: str) -> Optional[str]:
        with get_session() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id, chat_id=chat_id
            ).first()
            return record.profile if record else None

    def updateMemory(self, user_id: str, chat_id: str, summary: str, profile: str) -> None:
        with get_session() as session:
            record = session.query(ConversationMemory).filter_by(
                user_id=user_id, chat_id=chat_id
            ).first()
            if record:
                record.summary    = summary
                record.profile    = profile
                record.updated_at = datetime.datetime.utcnow()
            else:
                session.add(ConversationMemory(
                    user_id=user_id, chat_id=chat_id,
                    summary=summary, profile=profile
                ))
            session.commit()

    # -------------------------------------------------------------------------
    # UserProfile
    # -------------------------------------------------------------------------

    def getUserProfile(self, user_id: str) -> Optional[UserProfile]:
        with get_session() as session:
            return session.query(UserProfile).filter_by(user_id=user_id).first()

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
        with get_session() as session:
            record = session.query(UserProfile).filter_by(user_id=user_id).first()
            if record:
                if summary                    is not None: record.summary                    = summary
                if profile                    is not None: record.profile                    = profile
                if preferedCommunicationStyle is not None: record.preferedCommunicationStyle = preferedCommunicationStyle
                if emotionalStabilityScore    is not None: record.emotionalStabilityScore    = emotionalStabilityScore
                if personalityType            is not None: record.personalityType            = personalityType
                if coachingStage              is not None: record.coachingStage              = coachingStage.value
                record.updated_at = datetime.datetime.utcnow()
            else:
                session.add(UserProfile(
                    user_id=user_id,
                    summary=summary,
                    profile=profile,
                    preferedCommunicationStyle=preferedCommunicationStyle,
                    emotionalStabilityScore=emotionalStabilityScore,
                    personalityType=personalityType,
                    coachingStage=coachingStage.value if coachingStage else None,
                ))
            session.commit()

    # -------------------------------------------------------------------------
    # UserStrength
    # -------------------------------------------------------------------------

    def addStrength(self, user_id: str, emotionLabel: str, frequency: int = 1) -> None:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return
            record = session.query(UserStrength).filter_by(
                userProfileId=profile.id, emotionLabel=emotionLabel
            ).first()
            if record:
                record.frequency  = (record.frequency or 0) + frequency
                record.updated_at = datetime.datetime.utcnow()
            else:
                session.add(UserStrength(
                    userProfileId=profile.id,
                    emotionLabel=emotionLabel,
                    frequency=frequency,
                ))
            session.commit()

    def getStrengths(self, user_id: str) -> list:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return []
            return session.query(UserStrength).filter_by(userProfileId=profile.id).all()

    # -------------------------------------------------------------------------
    # CoachingTag
    # -------------------------------------------------------------------------

    def addCoachingTag(self, user_id: str, tag: str, priority: TagPriority) -> None:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return
            exists = session.query(CoachingTag).filter_by(
                userProfileId=profile.id, tag=tag
            ).first()
            if not exists:
                session.add(CoachingTag(
                    userProfileId=profile.id,
                    tag=tag,
                    priority=priority.value,
                ))
                session.commit()

    def getCoachingTags(self, user_id: str) -> list:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return []
            return session.query(CoachingTag).filter_by(userProfileId=profile.id).all()

    # -------------------------------------------------------------------------
    # UserEmotion
    # -------------------------------------------------------------------------

    def addEmotion(self, user_id: str, emotionLabel: str, intensity: Optional[float] = None) -> None:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return
            session.add(UserEmotion(
                userProfileId=profile.id,
                emotionLabel=emotionLabel,
                intensity=intensity,
            ))
            session.commit()

    def getEmotionHistory(self, user_id: str) -> list:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return []
            return session.query(UserEmotion).filter_by(
                userProfileId=profile.id
            ).order_by(UserEmotion.detectedAt).all()

    # -------------------------------------------------------------------------
    # CoachingSession
    # -------------------------------------------------------------------------

    def addCoachingSession(
        self,
        user_id: str,
        chat_id: str,
        coachingStage: Optional[CoachingStage] = None,
        goalFocus: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> None:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return
            session.add(CoachingSession(
                userProfileId=profile.id,
                chat_id=chat_id,
                coachingStage=coachingStage.value if coachingStage else None,
                goalFocus=goalFocus,
                outcome=outcome,
            ))
            session.commit()

    def getCoachingSessions(self, user_id: str) -> list:
        with get_session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                return []
            return session.query(CoachingSession).filter_by(
                userProfileId=profile.id
            ).order_by(CoachingSession.createdAt).all()

    def updateCoachingSession(
        self,
        session_id: int,
        goalFocus: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> None:
        with get_session() as session:
            record = session.query(CoachingSession).filter_by(id=session_id).first()
            if not record:
                return
            if goalFocus is not None: record.goalFocus = goalFocus
            if outcome   is not None: record.outcome   = outcome
            session.commit()