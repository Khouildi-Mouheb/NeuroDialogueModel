import os
import chromadb
from typing import List, Any
from .vectorStore import VectorStore


class ChromaDBVectorStore(VectorStore):
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

        # ✅ THIS IS THE FIX
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
