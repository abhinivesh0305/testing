import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from elsai_ocr_extractors.config.loggerConfig import setup_logger
class AzureDocumentIntelligenceImplementation:
    """
    Class to handle document analysis using Azure Document Intelligence.
    """

    def __init__(self, file_path:str, vision_key: str = None, vision_endpoint: str = None):
        self.logger = setup_logger()
        # Set up API key and endpoint
        self.key = vision_key
        self.endpoint = vision_endpoint
        self.file_path = file_path
        # Initialize the Document Intelligence Client
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    def extract_text(self, pages: str = None) -> str:
        """
        Extracts text from a document with optional page selection.

        Args:
            
            pages (str, optional): Specific pages to analyze (e.g., "1,3"). Defaults to None.

        Returns:
            str: Extracted text content from the document.
        """

        self.logger.info("Starting text extraction from %s", self.file_path)
        try:

            with open(self.file_path, "rb") as f:
                self.logger.info("Opened file: %s", self.file_path)
                poller = self.client.begin_analyze_document(
                    model_id="prebuilt-layout",
                    body=f,
                    content_type="application/octet-stream",
                    pages=pages
                )

            self.logger.info("Analysis started for %s. Waiting for result...", self.file_path)
            # Get the result of the analysis
            result = poller.result()
            self.logger.info("Analysis completed for %s", self.file_path)
            ocr_output = result.as_dict()
            self.logger.info("Text extraction from %s completed successfully.", self.file_path)
            return ocr_output['content']

        except Exception as e:
            self.logger.error("Error while extracting text from %s: %s", self.file_path, e)
            raise
    def _extract_cell_data(self, table):
        cells = []
        for cell in table.cells:
            cells.append({
                "row_index": cell.row_index,
                "column_index": cell.column_index,
                "content": cell.content,
                "is_header": getattr(cell, "kind", None) == "columnHeader",
                "spans": getattr(cell, "column_span", 1)
            })
        return cells

    def _extract_page_numbers(self, table):
        pages = []
        if hasattr(table, "bounding_regions"):
            for region in table.bounding_regions:
                if region.page_number not in pages:
                    pages.append(region.page_number)
        return pages

    def _parse_table_data(self, result):
        tables = []
        if not result.tables:
            self.logger.info("No tables found.")
            return tables

        self.logger.info(f"Found {len(result.tables)} tables to extract")
        
        for idx, table in enumerate(result.tables):
            self.logger.info(f"Processing table {idx + 1} with {table.row_count} rows and {table.column_count} columns")
            table_data = {
                "table_id": idx,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "page_numbers": self._extract_page_numbers(table),
                "cells": self._extract_cell_data(table)
            }
            tables.append(table_data)
            self.logger.info(f"Extracted table {idx + 1} with {len(table_data['cells'])} cells")
        
        self.logger.info(f"Table extraction complete. Extracted {len(tables)} tables")
        return tables

    def extract_tables(self, pages: str = None):
        """
        Extracts tables from a document with optional page selection.
        
        Args:
            pages (str, optional): Specific pages to analyze (e.g., "1,3").
            
        Returns:
            list: List of dictionaries containing table data.
        """
        self.logger.info("Starting table extraction from %s", self.file_path)
        try:
            with open(self.file_path, "rb") as f:
                self.logger.info("Opened file: %s", self.file_path)
                poller = self.client.begin_analyze_document(
                    model_id="prebuilt-layout",
                    body=f,
                    content_type="application/octet-stream",
                    pages=pages
                )
            
            self.logger.info("Analysis started for %s. Waiting for result...", self.file_path)
            result = poller.result()
            self.logger.info("Analysis completed for %s", self.file_path)
            
            return self._parse_table_data(result)
        
        except Exception as e:
            self.logger.error("Error while extracting tables from %s: %s", self.file_path, e)
            raise

