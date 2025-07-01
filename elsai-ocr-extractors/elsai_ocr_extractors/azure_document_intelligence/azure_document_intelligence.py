from.implementation import AzureDocumentIntelligenceImplementation
import os
class AzureDocumentIntelligence:
    """
    Class to handle document analysis using Azure Document Intelligence.
    """

    def __init__(self, file_path:str, vision_key: str = None, vision_endpoint: str = None):


        vision_key = vision_key or os.getenv("VISION_KEY")
        vision_endpoint = vision_endpoint or os.getenv("VISION_ENDPOINT")
        if not vision_key or not vision_endpoint:
            raise ValueError("Azure Document Intelligence credentials (VISION_KEY and VISION_ENDPOINT) are missing. Please provide them as arguments or set them as environment variables.")
        self._impl = AzureDocumentIntelligenceImplementation(file_path=file_path, vision_key=vision_key, vision_endpoint=vision_endpoint)

    def extract_text(self, pages: str = None) -> str:
        """
        Extracts text from a document with optional page selection.

        Args:
            
            pages (str, optional): Specific pages to analyze (e.g., "1,3"). Defaults to None.

        Returns:
            str: Extracted text content from the document.
        """

        return self._impl.extract_text(pages=pages)

    def extract_tables(self, pages: str = None):
        """
        Extracts tables from a document with optional page selection.
        
        Args:
            pages (str, optional): Specific pages to analyze (e.g., "1,3"). Defaults to None.
            
        Returns:
            list: List of dictionaries containing table data.
        """
        return self._impl.extract_tables(pages=pages)
