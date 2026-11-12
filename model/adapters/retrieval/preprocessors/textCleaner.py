from .textPreprocessor import TextPreprocessor
from domain.entities.knowledge.document import Document

class TextCleaner(TextPreprocessor):

    def preprocessText(self, document : Document = None) -> Document:
        #basic example 
        cleaned_text = document.getContent().strip().lower()
        document.setCleanedContent(cleaned_text)
        return document