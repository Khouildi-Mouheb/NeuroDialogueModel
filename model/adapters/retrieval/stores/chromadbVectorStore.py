import os
import chromadb
from typing import Any
from ports.vectorStorePort import VectorStorePort


class ChromaDBVectorStore(VectorStorePort):
    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str | None = None
    ):
        if persist_directory is None:
            base_dir = os.path.dirname(__file__)
            persist_directory = os.path.join(base_dir, "chroma_store")
        persist_directory = os.path.abspath(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def addVector(self, vector: Any, metadata: dict | None = None, vector_id: str | None = None) -> None:
        if vector_id is None:
            vector_id = str(self.collection.count())

        self.collection.add(
            embeddings=[vector],
            metadatas=[metadata] if metadata else None,
            ids=[vector_id]
        )

    def query_vectors(self, query_vector: Any, top_k: int = 5):
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        return [
            {
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
            }
            for i in range(len(results["ids"][0]))
        ]
    


    def deleteDocument(self, document_id: str) -> int:
        """
        Delete all chunks from a specific document
        
        Args:
            document_id: The document ID to delete
            
        Returns:
            Number of chunks deleted
        """
        # First, query to get count of chunks to be deleted
        results = self.collection.get(  # Use self.collection, not self.vector_store.collection
            where={"document_id": document_id}
        )
        
        chunk_count = len(results["ids"]) if results["ids"] else 0
        
        if chunk_count > 0:
            # Delete all chunks from this document
            self.collection.delete(  # Use self.collection
                where={"document_id": document_id}
            )
            print(f"  Deleted {chunk_count} chunks from document {document_id}")
        else:
            print(f"  No chunks found for document {document_id}")
        
        return chunk_count