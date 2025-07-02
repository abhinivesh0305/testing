
from .implementation import CSVFileExtractorImplementation

class CSVFileExtractor:
    def __init__(self, file_path:str):
        self._impl = CSVFileExtractorImplementation(file_path)

    def load_from_csv(self):
        """
        Load data from a CSV file using CSVLoader.

        Returns:
            list: Extracted data from the CSV file.

        Raises:
            Exception: If the CSV file cannot be loaded.
        """
        return self._impl.load_from_csv()
