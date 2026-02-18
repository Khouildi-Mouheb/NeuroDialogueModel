"""
Emotion Detection Port - Abstraction for emotion analysis.

Defines the interface for emotion detection adapters.
"""
from abc import ABC, abstractmethod


class EmotionPort(ABC):
    """Abstract interface for emotion detection."""

    @abstractmethod
    def detect_emotions(self, text: str, top_k: int = 3):
        """
        Detect emotions in text.
        
        Args:
            text: Input text to analyze
            top_k: Number of top emotions to return
            
        Returns:
            EmotionResult containing detected emotions and scores
        """
        pass
