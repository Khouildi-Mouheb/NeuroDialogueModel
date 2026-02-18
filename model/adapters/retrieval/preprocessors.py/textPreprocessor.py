from abc import ABC , abstractmethod
from model.domain.entities.knowledge.document import Document

class TextPreprocessor(ABC):

    @abstractmethod
    def preprocessText(self,document : Document)->Document:
        pass