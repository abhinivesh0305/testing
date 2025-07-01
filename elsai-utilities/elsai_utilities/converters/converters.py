"""  
This module contains utility functions for converting documents.
"""

from .implementation import DocumentConverterImplementation

class DocumentConverter:
    """
    A class to convert documents from llama index format to langchain format.
    """
    
    def __init__(self):
        self._impl= DocumentConverterImplementation()
    
    def llama_index_to_langchain_document(self, llama_index_document, file_name=""):
        """
        Convert a llama index document to a langchain document.

        :param llama_index_document: The document in llama index format.
        :param file_name: The name of the file to be used as metadata.
        :return: A langchain document.
        """
        return self._impl.llama_index_to_langchain_document(llama_index_document, file_name)
