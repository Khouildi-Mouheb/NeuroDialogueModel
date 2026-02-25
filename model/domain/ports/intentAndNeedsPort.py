from abc import ABC, abstractmethod
from typing import List
from domain.valueObjects.intentAndNeedsResult import IntentAndNeedsResult


class IntentAndNeedsPort(ABC):
    """Port (interface) for any intent and psychological needs detection adapter.

    Any concrete agent that analyses user intents and needs must inherit
    from this class and implement all abstract methods.

    Usage:
        class IntentNeedsAgent(Agent, IntentPort):
            def detectIntents(self, text, top_k=None) -> List[str]: ...
            def detectNeeds(self, text, top_k=None) -> List[str]: ...
            def analyze(self, text) -> IntentAndNeedsResult: ...
    """

    @abstractmethod
    def detectIntents(self, text: str, top_k: int = None) -> List[str]:
        """Detect user intents from text.

        Args:
            text:  Raw user input.
            top_k: Number of top intents to return.

        Returns:
            List of top intent label values sorted by descending score.
        """
        ...

    @abstractmethod
    def detectNeeds(self, text: str, top_k: int = None) -> List[str]:
        """Detect psychological needs from text.

        Args:
            text:  Raw user input.
            top_k: Number of top needs to return.

        Returns:
            List of top need label values sorted by descending score.
        """
        ...

    @abstractmethod
    def analyze(self, text: str) -> IntentAndNeedsResult:
        """Run both detections and return a combined result.

        Args:
            text: Raw user input.

        Returns:
            IntentAndNeedsResult containing detected intents and needs.
        """
        ...