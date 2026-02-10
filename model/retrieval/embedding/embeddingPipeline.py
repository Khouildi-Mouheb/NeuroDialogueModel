from model.retrieval.domain.chunk import Chunk
from model.retrieval.domain.document import Document
from infrastructure.chunking.fixedSizeChunker import FixedSizeChunker
from infrastructure.chunking.textChunk import TextChunk
from infrastructure.embedding.embeddingModel import EmbeddingModel
from infrastructure.preprocessors.textPreprocessor import TextPreprocessor
from infrastructure.preprocessors.textCleaner import TextCleaner
from infrastructure.documentLoading.documentLoader import DocumentLoader
from infrastructure.documentLoading.onlineDocumentLoader import OnlineDocumentLoader
from infrastructure.documentLoading.PDFDocumentLoader import PDFDocumentLoader
from infrastructure.rerieval.chromadbVectorStore import ChromaDBVectorStore


class EmbeddingPipeLine:
    def __init__(
            self,
            loader : DocumentLoader,
            textPreprocessor : TextPreprocessor,
            textChunker : TextChunk,
            embeddingModel : EmbeddingModel,

            ) :
        self.document=None
        self.documentLoader=loader
        self.textPreprocessor=textPreprocessor
        self.textChunker=textChunker
        self.embeddingModel=embeddingModel


    def embedDocument(self , docsource : str):
        document=self.documentLoader.loadDocument(docsource)
        document = self.textPreprocessor.preprocessText(document)
        document = self.textChunker.chunkText(document)
        document = self.embeddingModel.embedDocument(document)

        return document