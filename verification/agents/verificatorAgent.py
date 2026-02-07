# verification/agents/verificatorAgent.py
from abc import ABC, abstractmethod
from ...infrastructure.verification.domain import VerificationResult
from core.domain.userState import UserState

class VerificatorAgent(ABC):

    @abstractmethod
    def verify(self, query: str, response: str, user_state: UserState) -> VerificationResult:
        pass