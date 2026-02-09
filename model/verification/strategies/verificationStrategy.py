"""
Verification Strategy Base

Abstract base for verification strategies
"""

from abc import ABC, abstractmethod
from typing import List

from core.domain.userState import UserState
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from verification.domain.verificationStatus import VerificationStatus
from verification.agents.verificatorAgent import VerificatorAgent


class VerificationStrategy(ABC):
    """
    Strategy pattern for combining multiple verificators
    
    Different strategies can combine verificators in different ways
    """
    
    @abstractmethod
    def execute(
        self,
        verificators: List[VerificatorAgent],
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Execute verification strategy
        
        Args:
            verificators: List of verificators to run
            response: Response to verify
            query: User query for context
            user_state: User state for context
            
        Returns:
            Combined VerificationResult
        """
        pass