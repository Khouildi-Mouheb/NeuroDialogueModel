from core.domain.document import Document

class IDGenerator:
    @staticmethod
    def generateDocumentChunksId(document: Document):
        for idx, chunk in enumerate(document.getChunks(), start=1):
            new_id = f"doc{document.getId()}_chunk{idx}"
            chunk.setId(new_id)
