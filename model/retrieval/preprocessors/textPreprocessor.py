from abc import ABC , abstractmethod
from core.domain.document import Document

class TexrPreprocessor(ABC):

    @abstractmethod
    def preprocessText(self,document : Document)->Document:
        pass