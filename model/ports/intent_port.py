"""
Intent & Needs Detection Port - Abstraction for intent analysis.

Defines the interface for intent and needs detection adapters.
"""
from abc import ABC, abstractmethod


class IntentPort(ABC):
    """Abstract interface for intent and needs detection."""

    @abstractmethod
    def analyze(self, text: str):
        """
        Analyze intent and needs in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            IntentAndNeedsResult containing detected intents and needs
        """
        pass
