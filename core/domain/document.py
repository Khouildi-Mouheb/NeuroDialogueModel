from .chunk import Chunk
from typing import List

class Document:
    def __init__(self, id : int =0, source: str = "", content: str = "", metadata: list[str] =[] ):
        self.__id = id
        self.__source = source
        self.__content = content
        self.__metadata = metadata
        self.__numberofPages = 0
        self.__length = len(content)
        self.__cleanedText=""
        self.__chunks : List[Chunk] = []
        self.__numberOfChunks=len(self.__chunks)
        self.__embeddings=list()

    def setId(self, value):
        if value < 0:
            raise ValueError("ID cannot be negative")
        self.__id = value

    def getId(self):
        return self.__id
    
    def getSource(self):
        return self.__source
    
    def setSource(self, value):
        if not isinstance(value, str):
            raise ValueError("Source must be a string")
        self.__source = value
    
    def getcontent(self):
        return self.__content
    
    def setContent(self,content:str):
        self.__content=content
    
    def set(self, value):
        self.__content = value
        self.__length = len(value)


    def getMetadata(self):
        return self.__metadata
    
    def setMetadata(self, value):
        self.__metadata = value

    def setNumberofPages(self, value):
        if value < 0:
            raise ValueError("Number of pages cannot be negative")
        self.__numberofPages = value

    def getNumberofPages(self):
        return self.__numberofPages
    
    def getLength(self):
        return self.__length
    
    def setLength(self):
        self.__length = len(self.__content)

    
    def add_metadata(self, key: str, value):
        self.__metadata[key] = value
    
    def get_metadata(self, key: str, default=None):
        return self.__metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        return key in self.__metadata
    
    def update_metadata(self, new_metadata: dict):
        self.__metadata.update(new_metadata)

    def getCleanedContent(self):
        return self.__cleanedText
    
    def setCleanedContent(self, value):
        self.__cleanedText = value

    def getChunks(self):
        return self.__chunks
    
    def addChunk(self, chunk: Chunk):
        self.__chunks.append(chunk)
        self.__numberOfChunks = len(self.__chunks)

    def getNumberOfChunks(self):
        return self.__numberOfChunks
    
    def setEmbeddings(self, embeddings: list):
        self.__embeddings = embeddings

    def getEmbeddings(self):
        return self.__embeddings
    
    def docToDict(self):
        return {
            "id": self.__id,
            "source": self.__source,
            "content": self.__content[:100] + "..." if len(self.__content) > 100 else self.__content,
            "length": self.__length,
            "numberofPages": self.__numberofPages,
            "metadata": self.__metadata,
            "numberOfEmbeddings": len(self.__embeddings),
            "numberOfChunks": self.__numberOfChunks 
        }
    
    def __repr__(self):
        return f"Document(source='{self.__source}', length={self.__length}, pages={self.__numberofPages})"
    
    def __str__(self):
        return f"Document from {self.__source} ({self.__length} chars)"