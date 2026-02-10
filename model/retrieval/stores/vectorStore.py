from abc import ABC , abstractmethod
from typing import List, Any

class VectorStore(ABC):

    def addVectors(self, vectors: List[Any], metadata: List[dict]) -> None:
        """Add vectors with associated metadata to the vector store."""
        pass

    