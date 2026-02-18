from abc import ABC , abstractmethod
from model.retrieval.domain.document import Document

class TextPreprocessor(ABC):

    @abstractmethod
    def preprocessText(self,document : Document)->Document:
        pass