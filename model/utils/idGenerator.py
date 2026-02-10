from model.retrieval.domain.document import Document

class IDGenerator:
    @staticmethod
    def generateDocumentId(document: Document):
        document.setId(document.getSource())
