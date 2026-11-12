from abc import ABC , abstractmethod
from domain.entities.knowledge.document import Document

class DocumentLoader(ABC):

    @abstractmethod
    def loadDocument(self,source:str)->Document:
        pass