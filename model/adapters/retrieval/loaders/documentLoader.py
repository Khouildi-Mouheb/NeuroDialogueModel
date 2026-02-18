from abc import ABC , abstractmethod
from model.domain.entities.knowledge.document import Document

class DocumentLoader(ABC):

    @abstractmethod
    def loadDocument(self,source:str)->Document:
        pass