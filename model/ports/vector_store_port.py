"""
Vector Store Port - Abstraction for vector/semantic search storage.

Defines the interface for vector database adapters (ChromaDB, etc.)
"""
from abc import ABC, abstractmethod
from typing import List


class VectorStorePort(ABC):
    """Abstract interface for vector storage and retrieval."""

    @abstractmethod
    def add_documents(self, documents):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to store
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List:
        """
        Search vector store for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents/chunks
        """
        pass

    @abstractmethod
    def delete_all(self):
        """Delete all documents from store."""
        pass
