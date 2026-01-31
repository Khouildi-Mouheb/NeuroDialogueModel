from abc import ABC , abstractmethod
from core.domain.document import Document
from core.domain.chunk import Chunk


class TextChunk(ABC):
    @abstractmethod
    def chunkText(self,document : Document)->Document:
        pass