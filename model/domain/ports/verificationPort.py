from abc import ABC, abstractmethod
from typing import Optional
from domain.services.userState import UserState
from domain.valueObjects.verificationResult import VerificationResult


class VerificationPort(ABC):
    """Port (interface) for any verification adapter.

    Any concrete verificator must inherit from this class and implement
    the verify method.

    Usage:
        class EmpathyVerificator(Agent, VerificationPort):
            def verify(self, response, query, user_state) -> EmpathyVerificationResult: ...

        class AppropriatenessVerificator(Agent, VerificationPort):
            def verify(self, response, query, user_state) -> AppropriatenessVerificationResult: ...

        class SafetyVerificator(Agent, VerificationPort):
            def verify(self, response, query, user_state) -> SafetyVerificationResult: ...
    """

    @abstractmethod
    def verify(
        self,
        response: str,
        query: Optional[str] = None,
        user_state: Optional[UserState] = None,
    ) -> VerificationResult:
        """Verify a generated response.

        Args:
            response:   The generated response to verify.
            query:      Optional original user query for context.
            user_state: Optional user state (emotions, intents, needs).

        Returns:
            A VerificationResult subclass with the verification outcome.
        """
        ...