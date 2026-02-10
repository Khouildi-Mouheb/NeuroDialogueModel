from model.retrieval.loaders.documentLoader import DocumentLoader
from model.retrieval.preprocessing.textPreprocessor import TextPreprocessor
from model.retrieval.chunking.textChunk import TextChunk
from model.retrieval.embedding.embeddingModel import EmbeddingModel
from model.retrieval.indexing.documentIndexer import DocumentIndexer
from model.retrieval.domain.document import Document
from model.utils.idGenerator import IDGenerator

class EmbeddingPipeline:

    
    def __init__(
        self,
        loader: DocumentLoader,
        textPreprocessor: TextPreprocessor,
        textChunker: TextChunk,
        embeddingModel: EmbeddingModel,
        indexer: DocumentIndexer = None ,
        docIdGenerator=IDGenerator,
    ):
        self.documentLoader = loader
        self.textPreprocessor = textPreprocessor
        self.textChunker = textChunker
        self.embeddingModel = embeddingModel
        self.indexer = indexer
        self.docIdGenerator=docIdGenerator
    
    def process(
        self,
        document_source: str,
        index_immediately: bool = True
        ) -> Document:

        print(f"\n{'='*70}")
        print(f"Processing: {document_source}")
        print(f"{'='*70}")
        
        # Step 1: Load
        print("1. Loading document...")
        document = self.documentLoader.loadDocument(document_source)
        print(f"   ✅ Loaded ({document.getLength()} characters)")
        self.docIdGenerator.generateDocumentId(document)
        print(f'document ID = {document.getId()}')

        # Step 2: Preprocess
        print("2. Preprocessing...")
        document = self.textPreprocessor.preprocessText(document)
        print(f"   ✅ Cleaned")
        
        # Step 3: Chunk
        print("3. Chunking...")
        document = self.textChunker.chunkText(document)
        print(f"   ✅ Created {document.getNumberOfChunks()} chunks")
        
        # Step 4: Embed
        print("4. Embedding...")
        document = self.embeddingModel.embedDocument(document)
        print(f"   ✅ Embedded {document.getNumberOfChunks()} chunks")
        
        # Step 5: Index (optional)
        if index_immediately and self.indexer:
            print("5. Indexing...")
            self.indexer.indexDocument(document)
            print(f"   ✅ Indexed")
        
        print(f"{'='*70}")
        print(f"✅ Processing complete!")
        print(f"{'='*70}\n")
        
        return document
    
    def processMultiple(
        self,
        document_sources: list[str],
        index_immediately: bool = True
    ) -> list[Document]:

        documents = []
        
        for source in document_sources:
            document = self.process(source, index_immediately)
            documents.append(document)
        
        return documents


