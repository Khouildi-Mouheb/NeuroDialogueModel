"""ChromaDB Vector Store Adapter - Implements VectorStorePort using ChromaDB."""
from typing import List
from ports.vector_store_port import VectorStorePort


class ChromaDBVectorStore(VectorStorePort):
    """ChromaDB implementation of VectorStorePort for semantic search."""
    
    def __init__(self, collection_name: str = "documents", persist_directory: str = None):
        try:
            import chromadb
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        except ImportError:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
    
    def add_documents(self, documents: List[dict]):
        """Add documents to ChromaDB collection."""
        ids = []
        documents_text = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            if isinstance(doc, dict):
                doc_id = doc.get("id", f"doc_{i}")
                text = doc.get("text", str(doc))
                metadata = doc.get("metadata", {})
            else:
                doc_id = f"doc_{i}"
                text = str(doc)
                metadata = {}
            
            ids.append(doc_id)
            documents_text.append(text)
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            documents=documents_text,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = 5) -> List:
        """Search ChromaDB for relevant documents."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Transform ChromaDB results to standard format
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    distance = results.get("distances", [[]])[0][i] if results.get("distances") else None
                    metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
                    
                    documents.append({
                        "text": doc,
                        "score": 1 - distance if distance is not None else 0.0,
                        "metadata": metadata
                    })
            
            return documents
        except Exception as e:
            print(f"ChromaDB search error: {e}")
            return []
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.chroma_client.delete_collection(name=self.collection.name)
        except Exception as e:
            print(f"Error deleting collection: {e}")
