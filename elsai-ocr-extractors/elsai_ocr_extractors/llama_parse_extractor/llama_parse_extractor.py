from .implementation import LlamaParseExtractorImplementation

class LlamaParseExtractor:
    """
    A class to interact with the LlamaParse library for loading and extracting data from files.
    """
    def __init__(self, **kwargs):
        self._impl = LlamaParseExtractorImplementation(**kwargs)

    def load_csv(self, csv_file_path):
        """
        Loads data from a CSV file using LlamaParse.

        Args:
            csv_file_path (str): Path to the CSV file.

        Returns:
            Any: Parsed data returned by LlamaParse.
        """
        return self._impl.load_csv(csv_file_path=csv_file_path)
