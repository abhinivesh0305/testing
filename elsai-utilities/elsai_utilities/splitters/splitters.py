"""
This module provides utilities for splitting documents into chunks.
"""
from .implementation import DocumentChunkerImplementation
from langchain_core.documents import Document
class DocumentChunker:
    """
    Class for chunking content into pages and returning as Document objects with metadata.
    """

    def __init__(self):
        self._impl = DocumentChunkerImplementation()

    def chunk_page_wise(self, contents: str, file_name: str) -> list:
        """
        Splits the contents into chunks when there are two or more consecutive
        newline characters and returns each section as a Document object with
        page numbers and filename in the metadata

        Args:
            contents (str): Input text
            file_name (str): Name of the file

        Returns:
            list: list of text chunks
        """
        return self._impl.chunk_page_wise(contents, file_name)

    def chunk_markdown_header_wise(
        self,
        text: str = "",
        file_name: str = "",
        headers_to_split_on: list[tuple[str, str]] = None,
        strip_headers: bool = True,
    ) -> list[str]:
        """
        Split the text into markdown headers.
        """
        return self._impl.chunk_markdown_header_wise(
            text=text,
            file_name=file_name,
            headers_to_split_on=headers_to_split_on,
            strip_headers=strip_headers
        )


    def chunk_recursive(
        self,
        contents: str,
        file_name: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> list[Document]:
        """
        Splits the document into overlapping chunks using RecursiveCharacterTextSplitter.

        Args:
            contents (str): Input text to split
            file_name (str): Name of the file
            chunk_size (int): Maximum characters per chunk
            chunk_overlap (int): Overlapping characters between chunks

        Returns:
            list: List of Document objects with metadata
        """
        return self._impl.chunk_recursive(
            contents=contents,
            file_name=file_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )