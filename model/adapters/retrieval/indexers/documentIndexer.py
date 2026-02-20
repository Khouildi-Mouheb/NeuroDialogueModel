
from domain.entities.knowledge.document import Document
from ports.vectorStorePort import VectorStorePort



class DocumentIndexer:
    """
    Indexes documents into vector store
    
    Responsibility:
    - Take processed document (with chunks + embeddings)
    - Store each chunk in vector database
    - Store metadata for retrieval
    
    Usage:
    indexer = DocumentIndexer(vector_store)
    indexer.indexDocument(processed_document)
    """
    
    def __init__(self, vector_store: VectorStorePort):
        """
        Args:
            vector_store: Vector database to store chunks
        """
        self.vector_store = vector_store
    
    def indexDocument(self, document: Document) -> int:
        """
        Index all chunks from a document
        
        Args:
            document: Document with chunks and embeddings
            
        Returns:
            Number of chunks indexed
        """
        chunks = document.getChunks()
        indexed_count = 0
        
        for chunk in chunks:
            # Get embedding
            embedding = chunk.getEmbedding()
            
            if embedding is None:
                print(f"Warning: Chunk {chunk.getId()} has no embedding, skipping")
                continue
            
            # Prepare metadata
            metadata = {
                "chunk_id": chunk.getId(),
                "document_id": document.getId(),
                "document_source": document.getSource(),
                "chunk_index": chunk.getChunkIndex(),
                "text": chunk.getText(),
                "start_index": chunk.getStartIndex(),
                "end_index": chunk.getEndIndex(),
                **chunk.getMetadata()  # Include chunk's own metadata
            }
            
            # Add to vector store
            self.vector_store.addVector(
                vector=embedding,
                metadata=metadata,
                vector_id=chunk.getId()
            )
            
            indexed_count += 1
        
        print(f"✅ Indexed {indexed_count} chunks from {document.getSource()}")
        return indexed_count
    
    def indexMultipleDocuments(self, documents: list[Document]) -> int:

        total_indexed = 0
        
        for document in documents:
            count = self.indexDocument(document)
            total_indexed += count
        
        return total_indexed