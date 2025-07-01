"""
This module provides utilities for splitting documents into chunks.
"""
import re
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from elsai_utilities.config.loggerConfig import setup_logger

class DocumentChunkerImplementation:
    """
    Class for chunking content into pages and returning as Document objects with metadata.
    """

    def __init__(self):
        self.logger = setup_logger()

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
        self.logger.debug("Starting to chunk the document")
        pages = re.split(r'\n\n+', contents)
        document_pages = []
        for index, page in enumerate(pages):
            self.logger.debug("Processing page %d", index + 1)
            document = Document(page_content=page, metadata={"page_number": index + 1, "source": file_name})
            document_pages.append(document)

        self.logger.info("Document chunking completed. %d pages processed.", len(document_pages))
        return document_pages

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
        if headers_to_split_on is None:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=strip_headers)
        split_text = markdown_splitter.split_text(text)
        for item in split_text:
            item.metadata["source"] = file_name
        return split_text


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
        self.logger.debug("Starting recursive character-wise splitting")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = splitter.split_text(contents)
        documents = [
            Document(page_content=chunk, metadata={"source": file_name, "chunk_index": i + 1})
            for i, chunk in enumerate(splits)
        ]

        self.logger.info("Recursive chunking completed. %d chunks created.", len(documents))
        return documents