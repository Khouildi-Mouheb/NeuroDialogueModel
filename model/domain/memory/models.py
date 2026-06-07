from sqlalchemy import Column, Integer, Text, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


# Stores per-session conversation summaries and snapshots, linked by user and chat identifiers.
class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(String, nullable=False, index=True)
    chat_id    = Column(String, nullable=False, index=True)
    summary    = Column(Text, nullable=True)
    profile    = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


# Stores the global, persistent profile of a user including personality, coaching stage, and a cached emotional stability score.
class UserProfile(Base):
    __tablename__ = "user_profile"

    id                         = Column(Integer, primary_key=True)
    user_id                    = Column(String, nullable=False, index=True)
    summary                    = Column(Text, nullable=True)
    profile                    = Column(Text, nullable=True)
    preferedCommunicationStyle = Column(Text, nullable=True)
    emotionalStabilityScore    = Column(Float, nullable=True)
    personalityType            = Column(Text, nullable=True)
    coachingStage              = Column(Text, nullable=True)
    updated_at                 = Column(DateTime, default=datetime.utcnow)

    strengths      = relationship("UserStrength", back_populates="user_profile")
    coaching_tags  = relationship("CoachingTag",  back_populates="user_profile")
    emotions       = relationship("UserEmotion",  back_populates="user_profile")
    sessions       = relationship("CoachingSession", back_populates="user_profile")


# Tracks recurring strengths or positive patterns observed for a user, with their frequency of appearance.
class UserStrength(Base):
    __tablename__ = "user_strength"

    id            = Column(Integer, primary_key=True)
    userProfileId = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    emotionLabel  = Column(Text, nullable=True)
    frequency     = Column(Integer, nullable=True)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    user_profile = relationship("UserProfile", back_populates="strengths")


# Stores coaching focus areas assigned to a user, each with a priority level.
class CoachingTag(Base):
    __tablename__ = "coaching_tag"

    id            = Column(Integer, primary_key=True)
    userProfileId = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    tag           = Column(Text, nullable=True)
    priority      = Column(Text, nullable=True)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    user_profile = relationship("UserProfile", back_populates="coaching_tags")


# Records each emotion detected during a conversation, with its intensity score, enabling emotional history tracking.
class UserEmotion(Base):
    __tablename__ = "user_emotion"

    id            = Column(Integer, primary_key=True)
    userProfileId = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    emotionLabel  = Column(Text, nullable=False)
    intensity     = Column(Float, nullable=True)
    detectedAt    = Column(DateTime, default=datetime.utcnow)

    user_profile = relationship("UserProfile", back_populates="emotions")


# Captures a snapshot of each coaching session, linking it to a conversation and recording the stage, goal, and outcome.
class CoachingSession(Base):
    __tablename__ = "coaching_session"

    id            = Column(Integer, primary_key=True)
    userProfileId = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    chat_id       = Column(String, nullable=False)
    coachingStage = Column(Text, nullable=True)
    goalFocus     = Column(Text, nullable=True)
    outcome       = Column(Text, nullable=True)
    createdAt     = Column(DateTime, default=datetime.utcnow)

    user_profile = relationship("UserProfile", back_populates="sessions")