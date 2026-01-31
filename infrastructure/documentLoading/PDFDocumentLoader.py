from .documentLoader import DocumentLoader
from core.domain.document import Document
import PyPDF2 


class PDFDocumentLoader(DocumentLoader):

    def loadDocument(self, source: str) -> Document:
        try:
            with open(source, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:  
                        text_parts.append(page_text)
                
                full_text = '\n'.join(text_parts)
                
                document = Document(source=source)
                document.setNumberofPages(len(reader.pages))
                document.setContent(full_text)
                document.setLength()
                """
                pdf_metadata = {
                    "file_type": "PDF",
                    "pdf_version": reader.metadata.get('/Producer', 'Unknown'),
                    "author": reader.metadata.get('/Author', 'Unknown'),
                    "title": reader.metadata.get('/Title', 'Unknown'),
                    "creation_date": str(reader.metadata.get('/CreationDate', 'Unknown')),
                    "number_of_pages": len(reader.pages),
                    "is_encrypted": reader.is_encrypted
                }
                """
                return document
                
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {source}")
        except PyPDF2.errors.PdfReadError:
            raise ValueError(f"Could not read PDF file: {source}. File may be corrupted.")
        except Exception as e:
            raise RuntimeError(f"Error loading PDF document: {str(e)}")