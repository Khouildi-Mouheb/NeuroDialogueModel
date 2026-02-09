"""
Base Verificator Agent

Abstract base class for all verificators
"""

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.userState import UserState
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from verification.domain.verificationStatus import VerificationStatus



class VerificatorAgent(ABC):
    """
    Base interface for all verificators
    
    All verificators must implement the verify method
    """
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Verify a generated response
        
        Args:
            response: The generated response to verify
            query: Optional user query for context
            user_state: Optional user state for context
            
        Returns:
            VerificationResult with verification outcome
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"