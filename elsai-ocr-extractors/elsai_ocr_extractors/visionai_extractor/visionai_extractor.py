from .implementation import VisionAIExtractorImplementation
import os



class VisionAIExtractor:
    """
    VisionAIPDFExtractor is a class that interacts with OpenAI Vision AI client
    to extract text from PDFs.
    """
    def __init__(self, api_key, model_name="gpt-4o"):

        api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("API key is required. Please set the OPENAI_API_KEY environment variable or pass it as an argument.")
        self._impl = VisionAIExtractorImplementation(api_key=api_key, model_name=model_name)

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a given PDF page using the 
        Vision AI client and returns as Langchain Documents.

        Args:
            pdf_path: The path to the PDF file.

        Returns:
            str: List of Langchain Documents containing the extracted text from each page.
        """
        return self._impl.extract_text_from_pdf(pdf_path=pdf_path)

    def __get_image_as_document(self, page_num, page_image, file_path):
        self._impl.__get_image_as_document(page_num=page_num, page_image=page_image, file_path=file_path)
