from typing import List, Optional
from domain.enums.orchestrationState import OrchestrationState
from application.config.systemComponents import SystemComponents


class EmbeddingOrchestrator:
    """Orchestrator for the full document indexing pipeline.

    Pipeline
    --------
    1. LOADING     — load raw document from source (PDF, URL, etc.)
    2. PREPROCESSING — clean and normalize text
    3. CHUNKING    — split into semantically coherent chunks
    4. EMBEDDING   — vectorize each chunk
    5. INDEXING    — store vectors + metadata in ChromaDB
    """

    def __init__(self, components: SystemComponents) -> None:
        self.components = components
        self.state = OrchestrationState.IDLE

    def _load(self, source: str):
        self.state = OrchestrationState.ANALYZING
        print(f"  [LOADING] {source}")
        return self.components.loader.loadDocument(source)

    def _preprocess(self, document):
        print(f"  [PREPROCESSING] {document.getSource()}")
        return self.components.preprocessor.preprocessText(document)

    def _chunk(self, document):
        print(f"  [CHUNKING] strategy: {self.components.chunker.__class__.__name__}")
        return self.components.chunker.chunkText(document)

    def _embed(self, document):
        self.state = OrchestrationState.EMBEDDING
        print(f"  [EMBEDDING] {len(document.getChunks())} chunks")
        return self.components.embedding_model.embedDocument(document)

    def _index(self, document) -> int:
        self.state = OrchestrationState.RETRIEVING
        print(f"  [INDEXING] storing in vector store...")
        return self.components.indexer.indexDocument(document)


    def indexDocument(self, source: str) -> int:
        
        print(f"\n  Starting indexing pipeline for: {source}")

        document   = self._load(source)
        document   = self._preprocess(document)
        document   = self._chunk(document)
        document   = self._embed(document)
        count      = self._index(document)

        self.state = OrchestrationState.COMPLETED
        print(f"  Done — {count} chunks indexed successfully.\n")
        return count

    def indexMultipleDocuments(self, sources: List[str]) -> int:
        """Run the full pipeline for multiple documents.

        Args:
            sources: List of file paths or URLs.

        Returns:
            Total number of chunks indexed across all documents.
        """
        total = 0
        for source in sources:
            total += self.indexDocument(source)
        print(f"  Total indexed: {total} chunks from {len(sources)} documents.")
        return total

    def deleteDocument(self, document_id: str) -> int:
        """Remove all chunks belonging to a document from the vector store.

        Args:
            document_id: The document ID to delete.

        Returns:
            Number of chunks deleted.
        """
        print(f"  [DELETING] document_id: {document_id}")
        count = self.components.vector_store.deleteDocument(document_id)
        print(f"  Deleted {count} chunks.")
        return count