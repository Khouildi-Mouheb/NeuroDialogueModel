from typing import Dict, Any, Optional, List

class Chunk:
    """
    Represents a chunk of text from a document
    
    Each chunk:
    - Has unique ID
    - Contains text snippet
    - Has position info (start/end)
    - Has its own embedding
    - References parent document
    - Has metadata
    """
    
    def __init__(
        self,
        id: str = "",
        text: str = "",
        document_id: Optional[int] = None,  # ADD: Link to parent document
        chunk_index: int = 0,  # ADD: Position in document
        start_index: int = 0,
        end_index: int = 0,
        metadata: Optional[Dict[str, Any]] = None,  # FIX: Dict not list
        embedding: Optional[List[float]] = None  # ADD: Store embedding
    ):
        self.__id = id
        self.__text = text
        self.__document_id = document_id
        self.__chunk_index = chunk_index
        self.__start_index = start_index
        self.__end_index = end_index
        self.__metadata = metadata if metadata is not None else {}
        self.__embedding = embedding  # Vector representation
    
    # ===== ID Methods =====
    def getId(self) -> str:
        return self.__id
    
    def setId(self, id: str):
        self.__id = id
    
    # ===== Text Methods =====
    def getText(self) -> str:
        return self.__text
    
    def setText(self, text: str):
        self.__text = text
    
    # ===== Document Reference =====
    def getDocumentId(self) -> Optional[int]:
        return self.__document_id
    
    def setDocumentId(self, doc_id: int):
        self.__document_id = doc_id
    
    # ===== Chunk Index =====
    def getChunkIndex(self) -> int:
        return self.__chunk_index
    
    def setChunkIndex(self, index: int):
        self.__chunk_index = index
    
    # ===== Position Methods =====
    def getStartIndex(self) -> int:
        return self.__start_index
    
    def getEndIndex(self) -> int:
        return self.__end_index
    
    def getLength(self) -> int:
        """Get length of chunk text"""
        return len(self.__text)
    
    # ===== Metadata Methods =====
    def getMetadata(self) -> Dict[str, Any]:
        return self.__metadata
    
    def setMetadata(self, metadata: Dict[str, Any]):
        self.__metadata = metadata
    
    def addMetadata(self, key: str, value: Any):
        """Add single metadata field"""
        self.__metadata[key] = value
    
    def getMetadataValue(self, key: str, default: Any = None) -> Any:
        """Get specific metadata value"""
        return self.__metadata.get(key, default)
    
    # ===== Embedding Methods =====
    def getEmbedding(self) -> Optional[List[float]]:
        """Get the vector embedding for this chunk"""
        return self.__embedding
    
    def setEmbedding(self, embedding: List[float]):
        """Set the vector embedding for this chunk"""
        self.__embedding = embedding
    
    def hasEmbedding(self) -> bool:
        """Check if chunk has an embedding"""
        return self.__embedding is not None
    
    # ===== Utility Methods =====
    def toDict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            "id": self.__id,
            "text": self.__text[:100] + "..." if len(self.__text) > 100 else self.__text,
            "document_id": self.__document_id,
            "chunk_index": self.__chunk_index,
            "start_index": self.__start_index,
            "end_index": self.__end_index,
            "length": self.getLength(),
            "has_embedding": self.hasEmbedding(),
            "metadata": self.__metadata
        }
    
    def __repr__(self) -> str:
        return f"Chunk(id='{self.__id}', length={self.getLength()}, index={self.__chunk_index})"
    
    def __str__(self) -> str:
        preview = self.__text[:50] + "..." if len(self.__text) > 50 else self.__text
        return f"Chunk {self.__chunk_index}: {preview}"