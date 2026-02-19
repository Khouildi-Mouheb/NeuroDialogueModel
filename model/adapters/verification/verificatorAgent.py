from abc import abstractmethod
from typing import Optional
from domain.entities.agent import Agent
from domain.services.userState import UserState
from domain.valueObjects.verificationResult import VerificationResult
from ports.verificationPort import VerificationPort


class VerificatorAgent(Agent, VerificationPort):
    """
    Abstract base class for all verificators.

    Inherits:
        Agent           — shared domain base (logging, identity, etc.)
        VerificationPort — enforces the verify() contract

    All verificators must implement the verify() method.
    """

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def verify(
        self,
        response: str,
        query: Optional[str] = None,
        user_state: Optional[UserState] = None,
    ) -> VerificationResult:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"