from .textChunk import TextChunk
from model.retrieval.domain.document import Document
from model.retrieval.domain.chunk import Chunk
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class SentenceChunker(TextChunk):
    """
    Sentence-Based Chunking
    
    How it works:
    - Split at sentence boundaries
    - Group N sentences per chunk
    - Natural breaks, preserves context
    
    Example:
    Text: "Sentence 1. Sentence 2. Sentence 3. Sentence 4."
    sentences_per_chunk = 2
    
    Result:
    - Chunk 1: "Sentence 1. Sentence 2."
    - Chunk 2: "Sentence 3. Sentence 4."
    """
    
    def __init__(
        self,
        sentences_per_chunk: int = 5,
        overlap_sentences: int = 1
    ):
        """
        Args:
            sentences_per_chunk: How many sentences in each chunk
            overlap_sentences: How many sentences overlap between chunks
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
    
    def chunkText(self, document: Document) -> Document:
        """Split document by sentences"""
        text = document.getCleanedContent()
        
        # Split into sentences
        sentences = nltk.sent_tokenize(text)
        
        # Group sentences into chunks
        current_position = 0
        chunk_index = 0
        
        i = 0
        while i < len(sentences):
            # Get sentences for this chunk
            end = min(i + self.sentences_per_chunk, len(sentences))
            chunk_sentences = sentences[i:end]
            chunk_text = ' '.join(chunk_sentences)
            
            # Find position in original text
            start_index = text.find(chunk_sentences[0], current_position)
            end_index = start_index + len(chunk_text)
            
            # Create chunk
            chunk = Chunk(
                id=f"{document.getId()}_chunk_{chunk_index}",
                text=chunk_text,
                document_id=document.getId(),
                chunk_index=chunk_index,
                start_index=start_index,
                end_index=end_index,
                metadata={
                    "chunking_strategy": "sentence",
                    "sentences_in_chunk": len(chunk_sentences),
                    "source": document.getSource()
                }
            )
            
            document.addChunk(chunk)
            
            # Move to next chunk (with overlap)
            i += self.sentences_per_chunk - self.overlap_sentences
            current_position = end_index
            chunk_index += 1
        
        return document
    
    def get_config(self) -> dict:
        return {
            "strategy": "sentence",
            "sentences_per_chunk": self.sentences_per_chunk,
            "overlap_sentences": self.overlap_sentences
        }