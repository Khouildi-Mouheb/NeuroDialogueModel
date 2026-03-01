from typing import Any, List, Dict, Optional
from domain.ports.vectorStorePort import VectorStorePort
from adapters.retrieval.embedding.embeddingModel import EmbeddingModel
from adapters.retrieval.agents.retrievalAgent import RetrievalAgent


class QueryRetriever(RetrievalAgent):
    """Retrieves relevant document chunks for a user query.

    Responsibilities:
        1. Embed the query using the embedding model
        2. Search the vector store for similar chunks
        3. Format and return ranked results

    Usage:
        retriever = QueryRetriever(vector_store, embedding_model)
        results   = retriever.retrieve("What's the refund policy?", top_k=5)
        context   = retriever.retrieveWithContext("What's the refund policy?")
    """

    def __init__(
        self,
        vector_store: VectorStorePort,
        embedding_model: EmbeddingModel,
    ) -> None:
        self.vector_store    = vector_store
        self.embedding_model = embedding_model



    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        queryType: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        query_embedding = self.embedding_model.embedText(query)

        raw_results = self.vector_store.query_vectors(
            query_vector=query_embedding,
            top_k=top_k,
            collection=queryType,
            filters=filters,
        )

        return [
            {
                "rank":             i + 1,
                "chunk_id":         result.get("id"),
                "text":             result.get("metadata", {}).get("text", ""),
                "source":           result.get("metadata", {}).get("document_source", ""),
                "similarity_score": 1 - result.get("distance", 1),  # distance → similarity
                "metadata":         result.get("metadata", {}),
            }
            for i, result in enumerate(raw_results)
        ]

    def retrieveWithContext(self, query: str, top_k: int = 5) -> str:
        """Retrieve and format results as a context string for the LLM.

        Args:
            query:  User's question.
            top_k:  Number of results to retrieve.

        Returns:
            Formatted context string ready to be injected into a prompt.
        """
        results = self.retrieve(query, top_k)

        context_parts = [
            f"[Document {r['rank']}] (Source: {r['source']})\n{r['text']}"
            for r in results
        ]

        return "\n---\n".join(context_parts)