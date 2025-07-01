from elsai_text_extractors.config.loggerConfig import setup_logger
from langchain_community.document_loaders import Docx2txtLoader

class DocxTextExtractorImplementation:
    """
    Extracts text from a DOCX file using Docx2txtLoader. 
    Handles file loading, text extraction, and error logging.
    """
    def __init__(self, file_path:str):
        self.logger = setup_logger()
        self.file_path = file_path

    def extract_text_from_docx(self) ->str:
        """
        Extracts text from a DOCX file.

        

        Returns:
            str: Extracted text content from the DOCX file.
        """


        try:
            self.logger.info("Starting docx extraction from %s", self.file_path)
            loader = Docx2txtLoader(self.file_path)
            data = loader.load()
            if(data is None or len(data) == 0):
                self.logger.warning("No content found in the DOCX file: %s", self.file_path)
                return "No content found in the DOCX file."
            return data[0].page_content
        except FileNotFoundError as e:
            self.logger.error("File not found: %s. Error: %s", self.file_path, e)
            return "Error: File not found."
        except ValueError as e:
            self.logger.error("Value error while processing %s: %s", self.file_path, e)
            return "Error: Invalid file format or content."
        except Exception as e:
            self.logger.error(
                "Unexpected error while extracting text from %s: %s", self.file_path, e
                )
            return f"An unexpected error occurred: {e}"
