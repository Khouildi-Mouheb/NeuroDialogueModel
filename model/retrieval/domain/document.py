from .chunk import Chunk
from typing import List, Dict, Any, Optional

class Document:

    def __init__(
        self, 
        id: int = 0, 
        source: str = "", 
        content: str = "", 
        metadata: Optional[Dict[str, Any]] = None  # FIX: Dict not list
    ):
        self.__id = id
        self.__source = source
        self.__content = content
        self.__metadata = metadata if metadata is not None else {}  # FIX: No mutable default
        self.__numberofPages = 0
        self.__length = len(content)
        self.__cleanedText = ""
        self.__chunks: List[Chunk] = []
        self.__numberOfChunks = 0
    
    # ===== ID Methods =====
    def setId(self, value: int):
        if value < 0:
            raise ValueError("ID cannot be negative")
        self.__id = value

    def getId(self) -> int:
        return self.__id
    
    # ===== Source Methods =====
    def getSource(self) -> str:
        return self.__source
    
    def setSource(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Source must be a string")
        self.__source = value
    
    # ===== Content Methods =====
    def getContent(self) -> str:  # FIX: Consistent naming
        return self.__content
    
    def setContent(self, content: str):
        self.__content = content
        self.__length = len(content)  # Auto-update length
    
    # ===== Metadata Methods =====
    def getMetadata(self) -> Dict[str, Any]:
        return self.__metadata
    
    def setMetadata(self, value: Dict[str, Any]):
        self.__metadata = value
    
    def addMetadata(self, key: str, value: Any):  # FIX: Consistent naming
        """Add or update a single metadata field"""
        self.__metadata[key] = value
    
    def getMetadataValue(self, key: str, default: Any = None) -> Any:
        """Get a specific metadata value"""
        return self.__metadata.get(key, default)
    
    def hasMetadata(self, key: str) -> bool:
        """Check if metadata key exists"""
        return key in self.__metadata
    
    def updateMetadata(self, new_metadata: Dict[str, Any]):
        """Update multiple metadata fields at once"""
        self.__metadata.update(new_metadata)
    
    # ===== Page Methods =====
    def setNumberOfPages(self, value: int):
        if value < 0:
            raise ValueError("Number of pages cannot be negative")
        self.__numberofPages = value

    def getNumberOfPages(self) -> int:
        return self.__numberofPages
    
    # ===== Length Methods =====
    def getLength(self) -> int:
        return self.__length
    
    # ===== Cleaned Content Methods =====
    def getCleanedContent(self) -> str:
        return self.__cleanedText
    
    def setCleanedContent(self, value: str):
        self.__cleanedText = value
    
    # ===== Chunk Methods =====
    def getChunks(self) -> List[Chunk]:
        return self.__chunks
    
    def addChunk(self, chunk: Chunk):
        """Add a chunk to the document"""
        self.__chunks.append(chunk)
        self.__numberOfChunks = len(self.__chunks)
    
    def getNumberOfChunks(self) -> int:
        return self.__numberOfChunks
    
    # ===== Utility Methods =====
    def toDict(self) -> Dict[str, Any]:  # FIX: Better naming
        """Convert document to dictionary for serialization"""
        return {
            "id": self.__id,
            "source": self.__source,
            "content": self.__content[:100] + "..." if len(self.__content) > 100 else self.__content,
            "length": self.__length,
            "numberOfPages": self.__numberofPages,
            "metadata": self.__metadata,
            "numberOfChunks": self.__numberOfChunks 
        }
    
    def __repr__(self) -> str:
        return f"Document(source='{self.__source}', length={self.__length}, pages={self.__numberofPages})"
    
    def __str__(self) -> str:
        return f"Document from {self.__source} ({self.__length} chars, {self.__numberOfChunks} chunks)"