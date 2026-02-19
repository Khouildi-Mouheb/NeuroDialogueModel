from abc import ABC, abstractmethod
from typing import Any, Optional


class VectorStore(ABC):
    """Port (interface) for any vector store adapter.

    Any concrete vector store must inherit from this class and implement
    all abstract methods.

    Usage:
        class ChromaDBVectorStore(VectorStore):
            def addVector(self, vector, metadata, vector_id) -> None: ...
            def query_vectors(self, query_vector, top_k) -> list: ...
            def deleteDocument(self, document_id) -> int: ...
    """

    @abstractmethod
    def addVector(
        self,
        vector: Any,
        metadata: Optional[dict] = None,
        vector_id: Optional[str] = None,
    ) -> None:
        """Store a vector with optional metadata.

        Args:
            vector:    The embedding vector to store.
            metadata:  Optional metadata dict associated with the vector.
            vector_id: Optional ID — auto-generated if not provided.
        """
        ...

    @abstractmethod
    def query_vectors(self, query_vector: Any, top_k: int = 5) -> list:
        """Search for the most similar vectors.

        Args:
            query_vector: The embedding to search with.
            top_k:        Number of results to return.

        Returns:
            List of dicts with id, distance, and metadata.
        """
        ...

    @abstractmethod
    def deleteDocument(self, document_id: str) -> int:
        """Delete all chunks belonging to a document.

        Args:
            document_id: The document ID whose chunks should be deleted.

        Returns:
            Number of chunks deleted.
        """
        ...