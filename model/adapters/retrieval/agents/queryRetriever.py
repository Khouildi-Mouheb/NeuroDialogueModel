
# retrieval/agents/queryRetriever.py

from model.ports.vectorStore import VectorStore
from model.adapters.retrieval.embedding.embeddingModel import EmbeddingModel
from typing import List, Dict, Any


class QueryRetriever:
    """
    Retrieves relevant documents for a query
    
    Responsibility:
    - Take user query
    - Embed query
    - Search vector store
    - Return relevant chunks
    
    Usage:
    retriever = QueryRetriever(vector_store, embedding_model)
    results = retriever.retrieve("What's the refund policy?", top_k=5)
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel
    ):
        """
        Args:
            vector_store: Vector database to search
            embedding_model: Model to embed queries
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User's question
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        # Step 1: Embed query
        query_embedding = self.embedding_model.embedtext(query)
        
        # Step 2: Search vector store
        results = self.vector_store.query_vectors(
            query_vector=query_embedding,
            top_k=top_k
        )
        
        # Step 3: Format results
        formatted_results = []
        for i, result in enumerate(results):
            formatted_results.append({
                "rank": i + 1,
                "chunk_id": result.get("id"),
                "text": result.get("metadata", {}).get("text", ""),
                "source": result.get("metadata", {}).get("document_source", ""),
                "similarity_score": 1 - result.get("distance", 1),  # Convert distance to similarity
                "metadata": result.get("metadata", {})
            })
        
        return formatted_results
    
    def retrieveWithContext(
        self,
        query: str,
        top_k: int = 5
    ) -> str:
        """
        Retrieve and format as context for LLM
        
        Args:
            query: User's question
            top_k: Number of results
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k)
        
        # Build context string
        context_parts = []
        for result in results:
            context_parts.append(
                f"[Document {result['rank']}] "
                f"(Source: {result['source']})\n"
                f"{result['text']}\n"
            )
        
        return "\n---\n".join(context_parts)
