from abc import ABC , abstractmethod
from core.domain.document import Document

class DocumentLoader(ABC):

    @abstractmethod
    def loadDocument(self,source:str)->Document:
        pass
