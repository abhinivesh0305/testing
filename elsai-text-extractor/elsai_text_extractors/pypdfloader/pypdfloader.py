from .implementation import PyPDFTextExtractorImplementation

class PyPDFTextExtractor:
    """
    A class to extract text content from PDF files using the PyPDFLoader library.
    This class handles the initialization of a logger, 
    loading the PDF file, and extracting its text content.
    """
    def __init__(self, file_path:str):
        self._impl = PyPDFTextExtractorImplementation(file_path)

    def extract_text_from_pdf(self)->str:
        """
            Extracts text from the PDF file.

            Returns:
                str: The extracted text or an error message.
        """
        return self._impl.extract_text_from_pdf()
