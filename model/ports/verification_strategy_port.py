"""
Verification Strategy Port - Abstraction for verification orchestration.

Defines the interface for combining multiple verification agents.
"""
from abc import ABC, abstractmethod
from typing import List


class VerificationStrategyPort(ABC):
    """Abstract interface for verification strategy orchestration."""

    @abstractmethod
    def execute(self, verificators: List, response: str, query: str = None, user_state = None):
        """
        Execute verification strategy using multiple verificators.
        
        Args:
            verificators: List of verification agents to use
            response: Generated response to verify
            query: Original user query
            user_state: User emotional/intent state
            
        Returns:
            VerificationResult with combined verification outcome
        """
        pass
