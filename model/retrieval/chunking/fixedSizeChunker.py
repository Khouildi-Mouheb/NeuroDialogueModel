from .textChunk import TextChunk
from model.retrieval.domain.chunk import Chunk
from typing import Dict, Any
from model.retrieval.domain.document import Document


#first and child class od textChunker (basic axample od chunking strategy)
class FixedSizeChunker(TextChunk):
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunkText(self, document: Document) -> Document:
        text = document.getCleanedContent()
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunk=Chunk(
                text=chunk_text,
                start_index=start,
                end_index=end
            )
            
            document.addChunk(chunk)
            start += self.chunk_size - self.overlap
        return document
    
    def get_config(self) -> Dict[str, Any]:
        return {
            "strategy": "fixed_size",
            "chunk_size": self.chunk_size,
            "overlap": self.overlap
        }
