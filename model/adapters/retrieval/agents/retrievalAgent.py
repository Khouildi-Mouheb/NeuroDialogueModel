from abc import abstractmethod
from typing import Any, List, Dict, Optional
from domain.entities.agent import Agent
from domain.ports.retrievalPort import RetrievalPort


class RetrievalAgent(Agent, RetrievalPort):
    """Abstract base class for all retrieval agents.

    Inherits:
        Agent        — shared domain base
        RetrievalPort — enforces the retrieve() contract

    All retrieval agents must implement retrieve() and retrieveWithContext().
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def retrieveWithContext(self, query: str, top_k: int = 5) -> str:
        ...