from application.chatOrchestrator import ChatOrchestrator
from application.embeddingOrchestrator import EmbeddingOrchestrator
from application.config.systemComponents import SystemComponents
from adapters.analysis.emotionDetectionAgent import EmotionDetectionAgent
from adapters.analysis.intentAndNeedsAgent import IntentNeedsAgent
from adapters.analysis.queryClassifierAdapter import QueryClassifierAdapter
from adapters.generation.cloudBasedGenerator import CloudBasedGenerator
from adapters.retrieval.agents.queryRetriever import QueryRetriever
from adapters.retrieval.embedding.embeddingModel import EmbeddingModel
from adapters.retrieval.stores.chromadbVectorStore import ChromaDBVectorStore
from adapters.retrieval.loaders.pdfDocumentLoader import PDFDocumentLoader
from adapters.retrieval.preprocessors.textCleaner import TextCleaner
from adapters.retrieval.chunkers.semanticChunker import SemanticChunker
from adapters.retrieval.indexers.documentIndexer import DocumentIndexer
from adapters.verification.empathyVerificator import EmpathyVerificator
from adapters.verification.appropriatenessVerificator import AppropriatenessVerificator
from adapters.verification.safetyVerificator import SafetyVerificator


COLLECTION_NAME = "neurodialogue"  


class ModelFactory:

    @staticmethod
    def buildChatOrchestrator() -> ChatOrchestrator:
        print("  [ModelFactory] Building ChatOrchestrator...")

        vector_store    = ChromaDBVectorStore(collection_name=COLLECTION_NAME)
        embedding_model = EmbeddingModel()

        components = SystemComponents(
            embedding_model = embedding_model,
            retriever       = QueryRetriever(
                                vector_store=vector_store,
                                embedding_model=embedding_model,
                              ),
            generator       = CloudBasedGenerator(),
            analysis_agents = [
                                EmotionDetectionAgent(),
                                IntentNeedsAgent(),
                                QueryClassifierAdapter(),
                               ],
            verifiers       = [
                                EmpathyVerificator(),
                                AppropriatenessVerificator(),
                                SafetyVerificator(),
                               ],
        )

        print("  [ModelFactory] ChatOrchestrator ready ✓")
        return ChatOrchestrator(components)

    @staticmethod
    def buildEmbeddingOrchestrator() -> EmbeddingOrchestrator:
        print("  [ModelFactory] Building EmbeddingOrchestrator...")

        vector_store    = ChromaDBVectorStore(collection_name=COLLECTION_NAME)
        embedding_model = EmbeddingModel()

        components = SystemComponents(
            embedding_model = embedding_model,
            loader          = PDFDocumentLoader(),
            preprocessor    = TextCleaner(),
            chunker         = SemanticChunker(),
            indexer         = DocumentIndexer(vector_store),
            vector_store    = vector_store,
        )

        print("  [ModelFactory] EmbeddingOrchestrator ready ✓")
        return EmbeddingOrchestrator(components)