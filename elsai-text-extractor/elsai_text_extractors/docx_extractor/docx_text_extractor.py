from .implementation import DocxTextExtractorImplementation

class DocxTextExtractor:
    """
    Extracts text from a DOCX file using Docx2txtLoader. 
    Handles file loading, text extraction, and error logging.
    """
    def __init__(self, file_path:str):
        self._impl = DocxTextExtractorImplementation(file_path)

    def extract_text_from_docx(self) ->str:
        """
        Extracts text from a DOCX file.

        

        Returns:
            str: Extracted text content from the DOCX file.
        """


        return self._impl.extract_text_from_docx()
