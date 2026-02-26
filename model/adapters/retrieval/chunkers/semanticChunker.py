from .textChunker import TextChunk
from domain.entities.knowledge.document import Document
from domain.entities.knowledge.chunk import Chunk
from typing import List
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')



class SemanticChunker(TextChunk):
    """
    Semantic Chunking Strategy
    
    How it works:
    1. Split text into sentences
    2. Calculate similarity between adjacent sentences
    3. When similarity drops (topic change), create new chunk
    4. Ensures chunks are semantically coherent
    
    Example:
    Text: "Our refund policy allows returns. Returns must be within 30 days. 
           We also sell electronics. Phones are very popular."
    
    Chunks:
    - Chunk 1: "Our refund policy... within 30 days" (refund topic)
    - Chunk 2: "We also sell electronics... very popular" (products topic)
    
    Better than fixed-size because it doesn't split mid-topic!
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.5,  # Lower = more splits
        min_chunk_size: int = 100,  # Minimum chars per chunk
        max_chunk_size: int = 1000,  # Maximum chars per chunk
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Args:
            similarity_threshold: Similarity below this = new chunk
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
            model_name: Sentence transformer model for embeddings
        """
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.model = SentenceTransformer(model_name)
    
    def chunkText(self, document: Document) -> Document:
        """
        Split document into semantically coherent chunks
        
        Process:
        1. Split into sentences
        2. Embed each sentence
        3. Calculate similarity between adjacent sentences
        4. Split when similarity drops
        """
        text = document.getCleanedContent()
        
        # Step 1: Split into sentences
        sentences = nltk.sent_tokenize(text)
        
        if len(sentences) == 0:
            return document
        
        # Step 2: Embed all sentences
        sentence_embeddings = self.model.encode(sentences)
        
        # Step 3: Calculate similarities and find split points
        chunks_text = self._create_semantic_chunks(
            sentences, 
            sentence_embeddings
        )
        
        # Step 4: Create Chunk objects
        current_position = 0
        for i, chunk_text in enumerate(chunks_text):
            start_index = text.find(chunk_text, current_position)
            end_index = start_index + len(chunk_text)
            
            chunk = Chunk(
                id=f"{document.getId()}_chunk_{i}",
                text=chunk_text,
                document_id=document.getId(),
                chunk_index=i,
                start_index=start_index,
                end_index=end_index,
                metadata={
                    "chunking_strategy": "semantic",
                    "source": document.getSource()
                }
            )
            
            document.addChunk(chunk)
            current_position = end_index
        
        return document
    
    def _create_semantic_chunks(
        self, 
        sentences: List[str], 
        embeddings: np.ndarray
    ) -> List[str]:
        """
        Group sentences into chunks based on semantic similarity
        
        Algorithm:
        1. Start with first sentence
        2. Add next sentence if similar enough
        3. If not similar, start new chunk
        4. Respect min/max size constraints
        """
        chunks = []
        current_chunk = [sentences[0]]
        current_length = len(sentences[0])
        
        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentence
            similarity = self._cosine_similarity(
                embeddings[i-1], 
                embeddings[i]
            )
            
            sentence_length = len(sentences[i])
            potential_length = current_length + sentence_length
            
            # Decision: Add to current chunk or start new one?
            should_continue = (
                similarity >= self.similarity_threshold and  # Similar enough
                potential_length <= self.max_chunk_size      # Not too long
            )
            
            should_split = (
                similarity < self.similarity_threshold or    # Topic changed
                potential_length > self.max_chunk_size or    # Too long
                current_length >= self.min_chunk_size        # Min size met
            )
            
            if should_continue and not should_split:
                # Add to current chunk
                current_chunk.append(sentences[i])
                current_length += sentence_length
            else:
                # Start new chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentences[i]]
                current_length = sentence_length
        
        # Add last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Returns value between -1 and 1:
        - 1 = identical
        - 0 = orthogonal (unrelated)
        - -1 = opposite
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_config(self) -> dict:
        """Get chunker configuration"""
        return {
            "strategy": "semantic",
            "similarity_threshold": self.similarity_threshold,
            "min_chunk_size": self.min_chunk_size,
            "max_chunk_size": self.max_chunk_size,
            "model": self.model
        }