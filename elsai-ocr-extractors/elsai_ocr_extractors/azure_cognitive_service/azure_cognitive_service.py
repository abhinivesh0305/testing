from .implementation import AzureCognitiveServiceImplementation
import os
class AzureCognitiveService:
    """
    A class to extract text from PDF files using Azure Cognitive Services' Read API.
    It handles authentication, text extraction, and error logging for the PDF processing.
    """
    def __init__(self, file_path:str, subscription_key: str = None, endpoint: str = None):


        subscription_key = subscription_key or os.getenv("AZURE_SUBSCRIPTION_KEY")
        endpoint = endpoint or os.getenv("AZURE_ENDPOINT")
        if not subscription_key or not endpoint:
            raise ValueError("Azure credentials (AZURE_SUBSCRIPTION_KEY AND AZURE_ENDPOINT) are missing. Please provide them as arguments or set them as environment variables.")
        self._impl = AzureCognitiveServiceImplementation(file_path=file_path, subscription_key=subscription_key, endpoint=endpoint)

    def extract_text_from_pdf(self) -> str:
        """
        Extracts text from a local PDF file using Azure Cognitive Services' Read API.
            
        Returns:
            str: Extracted text from the PDF or error message if the extraction fails.
        """
        return self._impl.extract_text_from_pdf()
