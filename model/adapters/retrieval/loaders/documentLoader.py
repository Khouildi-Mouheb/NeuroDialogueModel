from abc import ABC , abstractmethod
from model.retrieval.domain.document import Document

class DocumentLoader(ABC):

    @abstractmethod
    def loadDocument(self,source:str)->Document:
        pass