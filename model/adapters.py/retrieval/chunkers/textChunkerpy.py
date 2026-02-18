from abc import ABC , abstractmethod
from model.retrieval.domain.document import Document
from model.retrieval.domain.chunk import Chunk


class TextChunk(ABC):
    @abstractmethod
    def chunkText(self,document : Document)->Document:
        pass