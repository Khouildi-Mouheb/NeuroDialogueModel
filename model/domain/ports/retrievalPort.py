from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional


class RetrievalPort(ABC):
    """Port (interface) for any retrieval adapter.

    Any concrete retriever must inherit from this class and implement
    all abstract methods.

    Usage:
        class QueryRetriever(Agent, RetrievalPort):
            def retrieve(self, query, top_k, filters) -> List[Dict]: ...
            def retrieveWithContext(self, query, top_k) -> str: ...
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query.

        Args:
            query:   User's question.
            top_k:   Number of results to return.
            filters: Optional metadata filters to narrow search.

        Returns:
            List of dicts with rank, chunk_id, text, source,
            similarity_score, and metadata.
        """
        ...

    @abstractmethod
    def retrieveWithContext(self, query: str, top_k: int = 5) -> str:
        """Retrieve and format results as a single context string for the LLM.

        Args:
            query:  User's question.
            top_k:  Number of results to retrieve.

        Returns:
            Formatted context string ready to be injected into a prompt.
        """
        ...