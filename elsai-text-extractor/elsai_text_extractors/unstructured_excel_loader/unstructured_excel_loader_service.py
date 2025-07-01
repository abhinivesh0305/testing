from .implementation import UnstructuredExcelLoaderServiceImplementation
class UnstructuredExcelLoaderService:
    """
    A service for loading and extracting data from unstructured Excel files 
    using the UnstructuredExcelLoader library.
    """
    def __init__(self, file_path:str):
        self._impl = UnstructuredExcelLoaderServiceImplementation(file_path)

    def load_excel(self):
        """
        Load data from an unstructured Excel file using UnstructuredExcelLoader.

       
        Returns:
            list: Extracted documents from the Excel file.
            None: If an error occurs during loading.

        
        """
        return self._impl.load_excel()
