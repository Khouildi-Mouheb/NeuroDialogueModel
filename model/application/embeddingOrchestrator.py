from typing import Optional, List, Any
import os

from model.domain.entities.knowledge.document import Document


class EmbeddingOrchestrator:
    """Orchestrates loading, preprocessing, chunking, embedding and indexing.

    Components (dependency-injected):
    - loader: has `loadDocument(source)` -> Document
    - preprocessor: optional, has `preprocessText(document)` -> Document
    - chunker: optional, has `chunkText(document)` -> Document
    - embedding_model: has `embedDocument(document)` or `embedBatch(texts)`
    - indexer: optional, has `indexDocument(document)` OR
               vector_store: has `addVector(vector, metadata, vector_id)`

    The orchestrator is defensive: it will proceed with available
    components and report how many chunks were indexed.
    """

    def __init__(
        self,
        loader: Any,
        embedding_model: Any,
        preprocessor: Optional[Any] = None,
        chunker: Optional[Any] = None,
        indexer: Optional[Any] = None,
        vector_store: Optional[Any] = None,
    ) -> None:
        self.loader = loader
        self.preprocessor = preprocessor
        self.chunker = chunker
        self.embedding_model = embedding_model
        self.indexer = indexer
        self.vector_store = vector_store

    def _ensure_document(self, doc: Document) -> Document:
        # Basic sanity: make sure source and content exist
        if not isinstance(doc, Document):
            raise TypeError("loader must return a Document instance")
        if not doc.getContent() and not doc.getCleanedContent():
            raise ValueError("Document has no content")
        return doc

    def process_and_index(self, source: str) -> int:
        """Load document from `source`, preprocess, chunk, embed, and index.

        Returns: number of chunks indexed.
        """
        # 1. Load
        document = self.loader.loadDocument(source)
        document = self._ensure_document(document)

        # 2. Preprocess
        if self.preprocessor and hasattr(self.preprocessor, "preprocessText"):
            try:
                document = self.preprocessor.preprocessText(document)
            except Exception as e:
                # continue with original document but warn
                print(f"Preprocessing failed: {e}")

        # 3. Chunk
        if self.chunker and hasattr(self.chunker, "chunkText"):
            try:
                document = self.chunker.chunkText(document)
            except Exception as e:
                print(f"Chunking failed: {e}")

        # 4. Embed
        if hasattr(self.embedding_model, "embedDocument"):
            try:
                document = self.embedding_model.embedDocument(document)
            except Exception as e:
                print(f"Embedding document failed: {e}")
        else:
            # fallback: embed each chunk text via embedText/embedtext
            if hasattr(self.embedding_model, "embedText") or hasattr(self.embedding_model, "embedtext"):
                texts = [c.getText() for c in document.getChunks()]
                embeddings = []
                try:
                    if hasattr(self.embedding_model, "embedBatch"):
                        embeddings = self.embedding_model.embedBatch(texts)
                    else:
                        for t in texts:
                            if hasattr(self.embedding_model, "embedText"):
                                embeddings.append(self.embedding_model.embedText(t))
                            else:
                                embeddings.append(self.embedding_model.embedtext(t))
                    # attach embeddings
                    for chunk, emb in zip(document.getChunks(), embeddings):
                        chunk.setEmbedding(emb)
                except Exception as e:
                    print(f"Embedding chunks fallback failed: {e}")

        # 5. Index
        indexed = 0
        # Prefer indexer.indexDocument
        if self.indexer and hasattr(self.indexer, "indexDocument"):
            try:
                indexed = self.indexer.indexDocument(document)
                return indexed
            except Exception as e:
                print(f"Indexer failed: {e}")

        # Else, try vector_store direct indexing per-chunk
        if self.vector_store and hasattr(self.vector_store, "addVector"):
            for chunk in document.getChunks():
                emb = chunk.getEmbedding()
                if emb is None:
                    print(f"Skipping chunk {chunk.getId()} (no embedding)")
                    continue

                metadata = {
                    "chunk_id": chunk.getId(),
                    "document_id": document.getId(),
                    "document_source": document.getSource(),
                    "chunk_index": chunk.getChunkIndex(),
                    "text": chunk.getText(),
                    **(chunk.getMetadata() or {}),
                }

                try:
                    # many store adapters expect args (vector, metadata, vector_id)
                    try:
                        self.vector_store.addVector(vector=emb, metadata=metadata, vector_id=chunk.getId())
                    except TypeError:
                        # fallback to addVectors plural signature
                        if hasattr(self.vector_store, "addVectors"):
                            self.vector_store.addVectors([emb], [metadata])
                        else:
                            raise
                    indexed += 1
                except Exception as e:
                    print(f"Failed to index chunk {chunk.getId()}: {e}")

        print(f"Indexed {indexed} chunks from {document.getSource()}")
        return indexed

    def process_and_index_multiple(self, sources: List[str]) -> int:
        total = 0
        for s in sources:
            total += self.process_and_index(s)
        return total
