from .textPreprocessor import TexrPreprocessor
from model.retrieval.domain.document import Document

class TextCleaner(TexrPreprocessor):

    def preprocessText(self, document : Document = None) -> Document:
        #basic example 
        cleaned_text = document.getcontent().strip().lower()
        document.setCleanedContent(cleaned_text)
        return document