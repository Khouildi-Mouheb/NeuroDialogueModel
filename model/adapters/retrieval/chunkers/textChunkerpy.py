from abc import ABC , abstractmethod
from model.domain.entities.knowledge.document import Document
from model.domain.entities.knowledge.chunk import Chunk


class TextChunk(ABC):
    @abstractmethod
    def chunkText(self,document : Document)->Document:
        pass