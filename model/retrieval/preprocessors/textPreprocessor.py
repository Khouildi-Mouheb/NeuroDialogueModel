from abc import ABC , abstractmethod
from model.retrieval.domain.document import Document

class TexrPreprocessor(ABC):

    @abstractmethod
    def preprocessText(self,document : Document)->Document:
        pass