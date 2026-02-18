# retrieval/embedding/embeddingModel.py

import numpy as np
from sentence_transformers import SentenceTransformer
from model.domain.entities.knowledge.document import Document
from typing import List


class EmbeddingModel:
    """
    Generates vector embeddings for text
    
    Converts text to numerical vectors that capture meaning
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model_name: HuggingFace model name
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"✅ Loaded embedding model: {model_name} ({self.dimension} dimensions)")
    
    def embedDocument(self, document: Document) -> Document:
        """
        Embed all chunks in a document
        
        Each chunk gets its own embedding vector
        
        Args:
            document: Document with chunks (no embeddings yet)
            
        Returns:
            Document with chunks containing embeddings
        """
        chunks = document.getChunks()
        
        if not chunks:
            print(f"Warning: Document {document.getId()} has no chunks to embed")
            return document
        
        # Extract text from all chunks
        texts = [chunk.getText() for chunk in chunks]
        
        # Batch embed for efficiency
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Set embedding for each chunk
        for chunk, embedding in zip(chunks, embeddings):
            chunk.setEmbedding(embedding.tolist())
        
        print(f"✅ Embedded {len(chunks)} chunks from {document.getSource()}")
        return document
    
    def embedText(self, text: str) -> List[float]:
        """
        Embed a single piece of text (for queries)
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    # Keep your existing embedtext method for compatibility
    def embedtext(self, text: str) -> List[float]:
        """Alias for embedText (for compatibility)"""
        return self.embedText(text)
    
    def embedBatch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple texts efficiently
        
        Args:
            texts: List of texts to embed
            batch_size: Process this many at once
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
            embeddings.extend([emb.tolist() for emb in batch_embeddings])
        
        return embeddings
    
    def getSimilarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.embedText(text1)
        emb2 = self.embedText(text2)
        
        a = np.array(emb1)
        b = np.array(emb2)
        
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return float(similarity)
    
    def getDimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension