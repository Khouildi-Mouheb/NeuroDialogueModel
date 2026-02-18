"""
Verification Port - Abstraction for response verification.

Defines the interface for verification adapters (safety, empathy, etc.)
"""
from abc import ABC, abstractmethod


class VerificationPort(ABC):
    """Abstract interface for response verification."""

    @abstractmethod
    def verify(self, response: str, query: str = None, user_state = None):
        """
        Verify response quality/safety.
        
        Args:
            response: Generated response to verify
            query: Original user query (optional context)
            user_state: User emotional/intent state (optional context)
            
        Returns:
            VerificationResult with verification outcome
        """
        pass
