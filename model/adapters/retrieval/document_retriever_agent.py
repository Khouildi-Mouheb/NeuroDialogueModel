"""Document Retrieval Agent - Orchestrates document retrieval and chunking."""
from typing import List
from ports.vector_store_port import VectorStorePort
from domain.context.retriever_context import RetrieverContext


class DocumentRetrieverAgent:
    """Retrieves and manages document chunks for context generation."""
    
    def __init__(self, vector_store: VectorStorePort, chunk_size: int = 500, overlap: int = 50):
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def retrieve_documents(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieve relevant documents using semantic search."""
        return self.vector_store.search(query, top_k=top_k)
    
    def add_documents(self, documents: List[str]):
        """Add documents to the vector store."""
        chunks = []
        for doc in documents:
            doc_chunks = self._chunk_document(doc)
            chunks.extend(doc_chunks)
        
        self.vector_store.add_documents(chunks)
    
    def _chunk_document(self, document: str) -> List[dict]:
        """Split document into overlapping chunks."""
        chunks = []
        for i in range(0, len(document), self.chunk_size - self.overlap):
            chunk = document[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "start_idx": i,
                        "end_idx": i + len(chunk)
                    }
                })
        return chunks
    
    def create_retriever_context(self, query: str, top_k: int = 5) -> RetrieverContext:
        """Create RetrieverContext with retrieved documents."""
        documents = self.retrieve_documents(query, top_k=top_k)
        
        context = RetrieverContext()
        context.query = query
        context.retrieved_documents = documents
        context.chunk_count = len(documents)
        
        return context
